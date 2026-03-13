import dotenv from 'dotenv';
dotenv.config();
import express from 'express';
import cors from 'cors';
import connectDB from './config/db';
import otpRoutes from './routes/otpRoutes';
import logger from './utils/logger';
import { validateEmail } from './middleware';

const app = express();
const PORT = process.env.PORT || 3000;
let dbReady: Promise<any> | null = null;

function ensureDbConnection() {
  if (!dbReady) {
    dbReady = connectDB();
  }
  return dbReady;
}

app.use(cors());
app.set('trust proxy', true);
app.use(express.json());

// Ensure DB connection for both local server mode and Vercel serverless mode.
app.use(async (_req, _res, next) => {
  try {
    await ensureDbConnection();
    next();
  } catch (error) {
    logger.error('Database connection failed', error);
    next(error);
  }
});

app.get('/', (req: any, res: { send: (arg0: string) => void; }) => {
  res.send('Welcome to OTP service');
});

app.use('/api', validateEmail, otpRoutes);

async function startServer(): Promise<void> {
  try {
    await ensureDbConnection();
    app.listen(PORT, () => {
      logger.info(`Server is running on port ${PORT}`);
    });
  } catch (error) {
    logger.error('Failed to start server', error);
  }
}

// On Vercel, export the app for serverless handling; locally, run a normal server.
if (!process.env.VERCEL) {
  startServer();
}

export default app;