import { spawn } from 'node:child_process';
import { config } from 'dotenv';

config({ path: 'services/intelligence/.env', quiet: true });

if (!process.env.SUPABASE_JWT_SECRET) {
  console.error(
    'SUPABASE_JWT_SECRET is required for dev:intelligence. Set it in the shell or services/intelligence/.env. Use the Supabase project JWT secret, not the anon or service role key.',
  );
  process.exit(1);
}

const child = spawn(
  'uv',
  ['run', '--package', 'intelligence', 'uvicorn', 'app.main:app', '--reload', '--port', '8000'],
  {
    env: process.env,
    stdio: 'inherit',
    shell: process.platform === 'win32',
  },
);

for (const signal of ['SIGINT', 'SIGTERM']) {
  process.on(signal, () => {
    if (!child.killed) child.kill(signal);
  });
}

child.on('exit', (code) => {
  process.exit(code ?? 0);
});
