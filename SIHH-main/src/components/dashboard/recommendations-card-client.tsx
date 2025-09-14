'use client';

import type { GenerateRecommendationsOutput } from '@/ai/flows/generate-recommendations';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Check, X, RefreshCw, Lightbulb, Code, Shield, TrendingUp, Clock, BadgeCheck } from 'lucide-react';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';

type AugmentedRecommendation = GenerateRecommendationsOutput['recommendations'][0];

type RecommendationsCardClientProps = {
  recommendation: AugmentedRecommendation;
};

export default function RecommendationsCardClient({ recommendation }: RecommendationsCardClientProps) {
  const handleAccept = () => {
    console.log('Accepted:', recommendation);
  };

  const handleOverride = () => {
    console.log('Overridden:', recommendation);
  };

  const handleRequestAlternative = () => {
    console.log('Requesting alternative for:', recommendation);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence > 80) return 'bg-green-600';
    if (confidence > 60) return 'bg-yellow-500';
    return 'bg-orange-500';
  }
  
  const impactMap = {
    'Low': 'bg-green-500/20 text-green-700 border-green-500/30',
    'Medium': 'bg-yellow-500/20 text-yellow-700 border-yellow-500/30',
    'High': 'bg-red-500/20 text-red-700 border-red-500/30',
  };

  return (
    <Card className="flex flex-col justify-between flex-grow bg-gradient-to-br from-primary/5 via-transparent to-transparent">
      <CardContent className="p-4 space-y-4 text-sm">
        <div className="flex items-start gap-3">
          <Lightbulb className="w-5 h-5 text-primary mt-1 shrink-0" />
          <div>
            <h3 className="font-semibold text-foreground mb-1">Recommendation</h3>
            <p className="font-medium text-primary">{recommendation.recommendation}</p>
          </div>
        </div>
        
        <div className="flex items-start gap-3">
          <Code className="w-5 h-5 text-muted-foreground mt-1 shrink-0" />
          <div>
            <h3 className="font-semibold text-foreground mb-1">Reason</h3>
            <p className="text-muted-foreground">{recommendation.reason}</p>
          </div>
        </div>
        
        <div>
          <div className="flex justify-between items-center mb-2">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-muted-foreground shrink-0" />
                <h3 className="font-semibold text-foreground">Confidence</h3>
              </div>
              <span className="font-bold text-sm">{recommendation.confidence}%</span>
          </div>
          <Progress value={recommendation.confidence} className='h-2' indicatorClassName={getConfidenceColor(recommendation.confidence)} />
        </div>
        
        <div className='space-y-3 pt-2'>
            <div className='flex justify-between items-center'>
                <div className="flex items-center gap-2">
                    <BadgeCheck className="w-5 h-5 text-muted-foreground shrink-0" />
                    <h3 className="font-semibold text-foreground">Impact</h3>
                </div>
                <Badge className={`text-xs ${impactMap[recommendation.impact]}`}>{recommendation.impact}</Badge>
            </div>
             <div className='flex justify-between items-center'>
                <div className="flex items-center gap-2">
                    <Clock className="w-5 h-5 text-muted-foreground shrink-0" />
                    <h3 className="font-semibold text-foreground">Est. Time Saved</h3>
                </div>
                <span className='font-semibold text-sm'>{recommendation.timeSaving} mins</span>
            </div>
             <div className='flex justify-between items-center'>
                <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-muted-foreground shrink-0" />
                    <h3 className="font-semibold text-foreground">Punctuality Gain</h3>
                </div>
                 <span className='font-semibold text-sm text-green-600'>+{recommendation.performanceImprovement}%</span>
            </div>
        </div>

      </CardContent>
      
      <div className="p-4 pt-2 flex flex-wrap items-center justify-end gap-2">
        <Button variant="outline" size="sm" onClick={handleOverride} className="flex-grow sm:flex-grow-0">
          <X />
          Override
        </Button>
        <Button variant="outline" size="sm" onClick={handleRequestAlternative} className="flex-grow sm:flex-grow-0">
          <RefreshCw />
          Alternative
        </Button>
        <Button className="bg-primary/90 text-primary-foreground hover:bg-primary w-full sm:w-auto flex-grow-[2] sm:flex-grow-0" size="sm" onClick={handleAccept}>
          <Check />
          Accept
        </Button>
      </div>
    </Card>
  );
}
