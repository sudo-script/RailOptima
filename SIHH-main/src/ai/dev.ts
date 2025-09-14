'use server';
import { config } from 'dotenv';
config();

import '@/ai/flows/generate-recommendations.ts';
import '@/ai/flows/generate-video-flow.ts';
