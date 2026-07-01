import { test, expect, type Page } from '@playwright/test';
import { createClient } from '@supabase/supabase-js';

const APP_URL = 'http://localhost:5173';

function testEmail(prefix: string): string {
  return `${prefix}+${Date.now()}@test.studytracker.app`;
}

async function createTestUser(email: string, password: string): Promise<void> {
  const supabaseUrl = process.env.SUPABASE_URL!;
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
  const adminClient = createClient(supabaseUrl, serviceRoleKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
  await adminClient.auth.admin.createUser({ email, password, email_confirm: true });
}

async function signIn(page: Page, email: string, password: string): Promise<void> {
  await page.goto(`${APP_URL}/study/sign-in`);
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: /Continue|Sign in/i }).click();
  await page.waitForURL(/\/study\/(home|onboarding)/, { timeout: 10000 });
}

async function userDbName(page: Page): Promise<string> {
  return page.evaluate(async () => {
    const dbs = await indexedDB.databases();
    const userDb = dbs.find((db) => db.name?.startsWith('StudyTracker_'));
    if (!userDb?.name) throw new Error('No StudyTracker DB found');
    return userDb.name;
  });
}

async function seedEvents(page: Page, events: Array<{ kind: string; payload: Record<string, unknown>; createdAt: string }>): Promise<void> {
  const dbName = await userDbName(page);
  await page.evaluate(async ({ dbName, events }) => {
    const request = indexedDB.open(dbName);
    await new Promise<void>((resolve, reject) => {
      request.onsuccess = () => {
        const db = request.result;
        const tx = db.transaction('events', 'readwrite');
        const store = tx.objectStore('events');
        for (const event of events) store.add(event);
        tx.oncomplete = () => { db.close(); resolve(); };
        tx.onerror = () => reject(tx.error);
      };
      request.onerror = () => reject(request.error);
    });
  }, { dbName, events });
}

async function seedActiveSession(page: Page): Promise<void> {
  const dbName = await userDbName(page);
  await page.evaluate(async (dbName) => {
    const request = indexedDB.open(dbName);
    await new Promise<void>((resolve, reject) => {
      request.onsuccess = () => {
        const db = request.result;
        const tx = db.transaction('activeSession', 'readwrite');
        tx.objectStore('activeSession').put({
          id: 1,
          sessionId: crypto.randomUUID(),
          materialId: 'mat-1',
          sessionTitle: 'Linear Algebra Lecture 4',
          bookingId: 'booking-today',
          slotDate: new Date().toISOString().slice(0, 10),
          weekIndex: 0,
          plannedMinutes: 50,
          plannedSessionMinutes: 50,
          materialEstimatedMinutes: 120,
          startedAt: new Date().toISOString(),
          status: 'active',
          pauseIntervals: [],
          pomodoroConfig: { workMinutes: 50, breakMinutes: 10 },
          kind: 'manual',
        });
        tx.oncomplete = () => { db.close(); resolve(); };
        tx.onerror = () => reject(tx.error);
      };
      request.onerror = () => reject(request.error);
    });
  }, dbName);
}

async function seedOnboardingDraft(page: Page): Promise<void> {
  const dbName = await userDbName(page);
  await page.evaluate(async (dbName) => {
    const deadline = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
    const request = indexedDB.open(dbName);
    await new Promise<void>((resolve, reject) => {
      request.onsuccess = () => {
        const db = request.result;
        const tx = db.transaction('onboardingDraft', 'readwrite');
        tx.objectStore('onboardingDraft').put({
          id: 1,
          state: {
            deadline,
            purpose: 'Exam prep',
            weeklyHours: 6,
            weekdayHours: 1,
            weekendHours: 1,
            selectedStudyDays: ['Mon', 'Wed', 'Fri'],
            materials: [{
              id: 'mat-1',
              title: 'Linear Algebra Lecture 4',
              estimatedDuration: 120,
              role: 'anchor',
              additionOrder: 0,
              userOverrodeType: false,
              kind: 'manual',
              fetchStatus: 'success',
            }],
            playlists: [],
            previewEdits: [],
            stepReached: 3,
            nextAdditionOrder: 1,
          },
        });
        tx.oncomplete = () => { db.close(); resolve(); };
        tx.onerror = () => reject(tx.error);
      };
      request.onerror = () => reject(request.error);
    });
  }, dbName);
}

function todayEvents() {
  const now = new Date().toISOString();
  const today = now.slice(0, 10);
  return [
    {
      kind: 'MaterialAdded',
      payload: {
        materialId: 'mat-1',
        title: 'Linear Algebra Lecture 4',
        estimatedDuration: 120,
        kind: 'manual',
        role: 'anchor',
      },
      createdAt: now,
    },
    {
      kind: 'RoadmapCreated',
      payload: {
        startDate: today,
        deadline: today,
        weeks: 1,
        selectedStudyDays: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        weekdayHours: 2,
        weekendHours: 0,
        weeklyHours: 10,
        materialIds: ['mat-1'],
      },
      createdAt: now,
    },
    {
      kind: 'SessionBooked',
      payload: {
        roadmapCreatedAt: now,
        bookingId: 'booking-today',
        date: today,
        estimatedDuration: 50,
      },
      createdAt: now,
    },
  ];
}

test.describe('Material/session decoupling', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'app', 'app project only');
    if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_ROLE_KEY) test.skip();
  });

  test('Onboarding 3 new-roadmap URL renders booking summary without slot tie UI', async ({ page }) => {
    const email = testEmail('decoupled-onboarding');
    const password = 'TestPassword123!';
    await createTestUser(email, password);
    await signIn(page, email, password);
    await seedOnboardingDraft(page);

    await page.goto(`${APP_URL}/study/onboarding/3?new=1`);
    await expect(page.getByText('Projected finish')).toBeVisible();
    await expect(page.getByText('Your backlog fits your time')).toBeVisible();
    await expect(page.getByText('Linear Algebra Lecture 4')).toBeVisible();
    await expect(page.getByText('Pick one')).not.toBeVisible();
    await expect(page.getByText('Rest day')).not.toBeVisible();
  });

  test('Home starts at pre-session, then interrupt logs partial progress', async ({ page }) => {
    const email = testEmail('decoupled-session');
    const password = 'TestPassword123!';
    await createTestUser(email, password);
    await signIn(page, email, password);
    await seedEvents(page, todayEvents());

    await page.goto(`${APP_URL}/study/home`);
    await expect(page.getByText(/Suggested material/)).toBeVisible();
    await expect(page.getByText('Linear Algebra Lecture 4')).toBeVisible();

    await page.getByRole('button', { name: 'Start session' }).click();
    await expect(page.getByText('Ready to start')).toBeVisible();
    await page.getByLabel('Planned session length').evaluate((element) => {
      const input = element as HTMLInputElement;
      input.value = '35';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
    });
    await page.getByRole('button', { name: 'Start session' }).click();
    await expect(page.locator('.session-timer-display')).toBeVisible();

    await page.getByRole('button', { name: 'End session' }).click();
    await page.getByRole('button', { name: '75%' }).click();
    await page.getByRole('button', { name: 'Log session' }).click();

    const logged = await page.evaluate(async () => {
      const dbName = (await indexedDB.databases()).find((db) => db.name?.startsWith('StudyTracker_'))?.name;
      if (!dbName) return null;
      const request = indexedDB.open(dbName);
      return new Promise<Record<string, unknown> | null>((resolve, reject) => {
        request.onsuccess = () => {
          const db = request.result;
          const tx = db.transaction('events', 'readonly');
          const getAll = tx.objectStore('events').getAll();
          getAll.onsuccess = () => {
            const event = getAll.result.find((row: any) => row.kind === 'SessionLogged');
            db.close();
            resolve(event?.payload ?? null);
          };
          getAll.onerror = () => reject(getAll.error);
        };
        request.onerror = () => reject(request.error);
      });
    });

    expect(logged?.resolution).toBe('interrupted');
    expect(logged?.bookingId).toBe('booking-today');
    expect(logged?.materialPosition).toMatchObject({ kind: 'percent', value: 75 });
  });

  test('Continue bypasses pre-session setup when activeSession exists', async ({ page }) => {
    const email = testEmail('decoupled-continue');
    const password = 'TestPassword123!';
    await createTestUser(email, password);
    await signIn(page, email, password);
    await seedActiveSession(page);

    await page.goto(`${APP_URL}/study/session`);
    await expect(page.getByText('Ready to start')).not.toBeVisible();
    await expect(page.locator('.session-timer-display')).toBeVisible();
  });
});
