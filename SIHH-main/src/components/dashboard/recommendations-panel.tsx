import type { GenerateRecommendationsOutput } from '@/ai/flows/generate-recommendations';
import { Bot, Loader2 } from 'lucide-react';
import RecommendationsCardClient from './recommendations-card-client';
import { Card, CardContent } from '../ui/card';

type RecommendationsPanelProps = {
  recommendations: GenerateRecommendationsOutput['recommendations'];
  isLoading: boolean;
};

export default function RecommendationsPanel({ recommendations, isLoading }: RecommendationsPanelProps) {
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <Bot className="h-6 w-6 text-primary" />
        <h2 className="text-lg font-semibold text-foreground">AI Copilot</h2>
      </div>
      <div className="flex-grow flex flex-col space-y-3 overflow-y-auto max-h-[calc(80vh-100px)] pr-2">
        {isLoading ? (
           <div className="flex-grow flex items-center justify-center text-muted-foreground">
             <div className='text-center space-y-2'>
              <Loader2 className="h-8 w-8 animate-spin mx-auto" />
              <p>Analyzing network data...</p>
             </div>
           </div>
        ) : recommendations.length > 0 ? (
          recommendations.map((rec, index) => (
            <RecommendationsCardClient key={index} recommendation={rec} />
          ))
        ) : (
          <Card className="flex-grow flex items-center justify-center bg-muted/50">
            <CardContent className="p-4 text-center text-muted-foreground">
              <p>No active recommendations.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
