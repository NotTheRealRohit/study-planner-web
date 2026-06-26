import { mkdirSync } from 'node:fs';
import path from 'node:path';
import { test, expect, type Page } from '@playwright/test';
import { createClient } from '@supabase/supabase-js';

const APP_URL = 'http://localhost:5173';
const SCREENSHOT_DIR = path.resolve('e2e/__screens__/roadmap');

mkdirSync(SCREENSHOT_DIR, { recursive: true });

declare global {
  interface Window {
    __seed?: () => Promise<void>;
    __wipe?: () => Promise<void>;
  }
}

async function screenshot(page: Page, name: string): Promise<void> {
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, `${name}.png`),
    fullPage: true,
  });
}

async function createTestUser(email: string, password: string): Promise<void> {
  const supabaseUrl = process.env.SUPABASE_URL;
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!supabaseUrl || !serviceRoleKey) return;

  const adminClient = createClient(supabaseUrl, serviceRoleKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  });

  const { error } = await adminClient.auth.admin.createUser({
    email,
    password,
    email_confirm: true,
  });

  if (error && !error.message.includes('already been registered')) {
    throw error;
  }
}

function generateTestEmail(prefix: string): string {
  return `${prefix}+${Date.now()}@test.studytracker.app`;
}

async function signIn(page: Page, email: string, password: string): Promise<void> {
  await page.goto(`${APP_URL}/study/sign-in`);
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Continue' }).click();
  await page.waitForURL(/\/study\/(home|onboarding)/);
}

async function waitForDevSeeder(page: Page): Promise<void> {
  await page.waitForFunction(() => typeof window.__wipe === 'function');
}

async function insertEventsIntoFirstStudyDb(
  page: Page,
  events: Array<{ kind: string; payload: Record<string, unknown>; createdAt: string }>,
): Promise<void> {
  await page.evaluate(async (seedEvents) => {
    const databases = await indexedDB.databases();
    const dbName = databases.find((db) => db.name?.startsWith('StudyTracker_'))?.name;
    if (!dbName) throw new Error('StudyTracker IndexedDB not found');

    const db = await new Promise<IDBDatabase>((resolve, reject) => {
      const request = indexedDB.open(dbName);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });

    await new Promise<void>((resolve, reject) => {
      const tx = db.transaction('events', 'readwrite');
      const store = tx.objectStore('events');
      for (const event of seedEvents) store.add(event);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
      tx.onabort = () => reject(tx.error);
    });

    db.close();
  }, events);
}

async function insertOverflowSessionsForToday(page: Page): Promise<void> {
  const today = new Date().toISOString().slice(0, 10);
  const events = Array.from({ length: 4 }, (_, index) => {
    const startedAt = new Date(`${today}T1${index}:00:00`);
    const endedAt = new Date(startedAt.getTime() + (25 + index * 5) * 60000);
    return {
      kind: 'SessionLogged',
      payload: {
        sessionId: `overflow-${index}`,
        materialId: `overflow-material-${index}`,
        sessionTitle: `Overflow session ${index + 1}`,
        date: today,
        duration: 25 + index * 5,
        activeMinutes: 25 + index * 5,
        startedAt: startedAt.toISOString(),
        endedAt: endedAt.toISOString(),
        source: 'manual',
      },
      createdAt: endedAt.toISOString(),
    };
  });

  await insertEventsIntoFirstStudyDb(page, events);
}

test.describe('Roadmap calendar visual walkthrough', () => {
  test.use({ baseURL: APP_URL });

  test.beforeEach(() => {
    if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_ROLE_KEY) {
      test.skip();
    }
  });

  test('Phases 2-4: calendar grid, month navigation, and session modals', async ({ page }) => {
    const email = generateTestEmail('roadmap-calendar');
    const password = 'TestPassword123!';
    let currentMonthLabel = '';

    await createTestUser(email, password);
    await signIn(page, email, password);
    await waitForDevSeeder(page);

    await test.step('01-grid', async () => {
      await page.evaluate(async () => {
        await window.__wipe?.();
        await window.__seed?.();
      });
      await page.goto(`${APP_URL}/study/roadmap`);

      await expect(page.getByTestId('roadmap-calendar')).toBeVisible();
      currentMonthLabel = await page.getByTestId('roadmap-month-label').innerText();
      await expect(page.getByLabel(/Roadmap progress/i)).toBeVisible();
      await expect(page.getByLabel(/Roadmap status legend/i)).toBeVisible();
      const weekCount = await page.locator('.roadmap-week-row').count();
      expect(weekCount).toBeGreaterThanOrEqual(4);
      expect(weekCount).toBeLessThanOrEqual(6);
      await screenshot(page, '01-grid');
    });

    await test.step('02-status-colors', async () => {
      const todayCell = page.getByTestId('roadmap-today-cell');
      await expect(todayCell).toHaveClass(/roadmap-day-today/);
      await expect(todayCell).toContainText('Today');
      await expect(page.locator('.roadmap-day-current-week').first()).toBeVisible();

      const doneChip = page.locator('[data-status="done"][data-icon="ti-check"]').first();
      const pendingChip = page.locator('[data-status="pending"][data-icon="ti-clock"]').first();
      const skippedChip = page.locator('[data-status="skipped"][data-icon="ti-x"]').first();
      const unplannedLegend = page.locator('[data-status="unplanned"][data-icon="ti-plus"]').first();

      await expect(doneChip).toBeVisible();
      await expect(pendingChip).toBeVisible();
      await expect(skippedChip).toBeVisible();
      await expect(unplannedLegend).toBeVisible();
      await expect(page.locator('.terracotta-ring')).toHaveCount(0);
      await screenshot(page, '02-status-colors');
    });

    await test.step('03-empty', async () => {
      await page.evaluate(async () => {
        await window.__wipe?.();
      });
      await insertEventsIntoFirstStudyDb(page, [
        {
          kind: 'OnboardingCompleted',
          payload: {},
          createdAt: new Date().toISOString(),
        },
      ]);

      await page.goto(`${APP_URL}/study/roadmap`);
      await expect(page.getByTestId('roadmap-empty')).toBeVisible();
      await expect(page.getByRole('heading', { name: 'No active roadmap' })).toBeVisible();
      await screenshot(page, '03-empty');
    });

    await test.step('04-next-month', async () => {
      await page.evaluate(async () => {
        await window.__wipe?.();
        await window.__seed?.();
      });
      await insertOverflowSessionsForToday(page);
      await page.goto(`${APP_URL}/study/roadmap`);
      currentMonthLabel = await page.getByTestId('roadmap-month-label').innerText();

      await page.getByRole('button', { name: 'Next month' }).click();
      await expect(page.getByTestId('roadmap-month-label')).not.toHaveText(currentMonthLabel);
      await screenshot(page, '04-next-month');
    });

    await test.step('05-prev-month', async () => {
      await page.getByRole('button', { name: 'Previous month' }).click();
      await expect(page.getByTestId('roadmap-month-label')).toHaveText(currentMonthLabel);
      await screenshot(page, '05-prev-month');
    });

    await test.step('06-today-reset', async () => {
      const next = page.getByRole('button', { name: 'Next month' });
      const previous = page.getByRole('button', { name: 'Previous month' });

      while (await previous.isEnabled()) {
        await previous.click();
      }
      await expect(previous).toBeDisabled();

      while (await next.isEnabled()) {
        await next.click();
      }
      await expect(next).toBeDisabled();
      await expect(page.getByTestId('roadmap-deadline-marker')).toBeVisible();

      await page.getByRole('button', { name: 'Today' }).click();
      await expect(page.getByTestId('roadmap-month-label')).toHaveText(currentMonthLabel);
      await screenshot(page, '06-today-reset');
    });

    await test.step('07-hover-expand', async () => {
      const filledDay = page
        .locator('.roadmap-day-in-month')
        .filter({ has: page.locator('.roadmap-bubble') })
        .first();

      await filledDay.hover();
      await screenshot(page, '07-hover-expand');
    });

    await test.step('08-modal-done', async () => {
      await page.locator('.roadmap-bubble[data-status="done"]').first().click();
      await expect(page.getByRole('dialog', { name: 'Roadmap session detail' })).toBeVisible();
      await expect(page.getByText('Completed')).toBeVisible();
      await expect(page.getByRole('button', { name: 'View session' })).toBeVisible();
      await screenshot(page, '08-modal-done');
      await page.getByLabel('Close modal').click();
      await expect(page.getByRole('dialog', { name: 'Roadmap session detail' })).toHaveCount(0);
    });

    await test.step('09-modal-pending', async () => {
      await page.locator('.roadmap-bubble[data-status="pending"]').first().click();
      await expect(page.getByRole('dialog', { name: 'Roadmap session detail' })).toBeVisible();
      await expect(page.getByText('Planned')).toBeVisible();
      await expect(page.getByRole('button', { name: 'Start session' })).toBeVisible();
      await screenshot(page, '09-modal-pending');
      await page.getByLabel('Close modal').click();
      await expect(page.getByRole('dialog', { name: 'Roadmap session detail' })).toHaveCount(0);
    });

    await test.step('10-day-modal', async () => {
      await page
        .getByTestId('roadmap-today-cell')
        .getByRole('button', { name: /more/ })
        .click();
      await expect(page.getByRole('dialog', { name: 'Roadmap day sessions' })).toBeVisible();
      expect(await page.locator('.roadmap-day-list-row').count()).toBeGreaterThanOrEqual(4);
      await screenshot(page, '10-day-modal');
    });
  });
});
