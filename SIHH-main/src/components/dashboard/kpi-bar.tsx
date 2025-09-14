import { Card } from "@/components/ui/card";
import { ArrowUp, ArrowDown, Users, AlertCircle, Clock, Target, Gauge } from 'lucide-react';
import { Progress } from "../ui/progress";

type KpiData = {
  punctuality: { value: number; target: number, trend: number };
  avgDelay: { value: number; target: number, trend: number };
  activeTrains: { value: number; capacity: number, trend: number };
  disruptions: { value: number; last24h: number, trend: number };
}

type KpiBarProps = {
  data: KpiData;
}

export default function KpiBar({ data }: KpiBarProps) {
  return (
    <div className="bg-card/50 border-b">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 py-3">
          <KpiCard
            title="Punctuality"
            value={`${data.punctuality.value}%`}
            progress={data.punctuality.value}
            target={`Target: ${data.punctuality.target}%`}
            trend={data.punctuality.trend}
            icon={<Target className="h-5 w-5 text-muted-foreground" />}
          />
          <KpiCard
            title="Avg. Delay"
            value={`${data.avgDelay.value} min`}
            progress={(data.avgDelay.target - data.avgDelay.value) / data.avgDelay.target * 100}
            target={`Target: < ${data.avgDelay.target} min`}
            trend={data.avgDelay.trend}
            icon={<Clock className="h-5 w-5 text-muted-foreground" />}
            progressColor="bg-yellow-500"
          />
          <KpiCard
            title="Active Trains"
            value={data.activeTrains.value.toString()}
            progress={(data.activeTrains.value / data.activeTrains.capacity) * 100}
            target={`Total: ${data.activeTrains.value} trains`}
            trend={data.activeTrains.trend}
            icon={<Users className="h-5 w-5 text-muted-foreground" />}
            progressColor="bg-blue-500"
          />
          <KpiCard
            title="Disruptions (24h)"
            value={data.disruptions.value.toString()}
            progress={(data.disruptions.value / data.disruptions.last24h) * 100}
            target={`Total: ${data.disruptions.last24h}`}
            trend={data.disruptions.trend}
            icon={<AlertCircle className="h-5 w-5 text-muted-foreground" />}
            progressColor="bg-red-500"
          />
        </div>
      </div>
    </div>
  )
}

type KpiCardProps = {
  title: string;
  value: string;
  icon: React.ReactNode;
  progress: number;
  target: string;
  trend: number;
  progressColor?: string;
}

function KpiCard({ title, value, icon, progress, target, trend, progressColor = 'bg-primary' }: KpiCardProps) {
  const trendIsPositive = (title === 'Avg. Delay' || title.includes('Disruptions')) ? trend < 0 : trend > 0;
  const ChangeIcon = trend > 0 ? ArrowUp : ArrowDown;
  const changeColor = trendIsPositive ? 'text-green-600' : 'text-red-600';

  return (
    <Card className="p-4 flex flex-col justify-between shadow-none border-none bg-transparent">
      <div className="flex items-start justify-between mb-2">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <h3 className="text-2xl font-bold">{value}</h3>
        </div>
        {icon}
      </div>
       <div>
        <Progress value={progress} className="h-2 mb-1" indicatorClassName={progressColor} />
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>{target}</span>
           <div className="flex items-center">
            <ChangeIcon className={`h-3 w-3 mr-0.5 ${changeColor}`} />
            <span className={`${changeColor} font-semibold`}>{Math.abs(trend)}{title === 'Avg. Delay' ? 'm' : title === 'Punctuality' ? '%' : ''}</span>
          </div>
        </div>
      </div>
    </Card>
  )
}
