/**
 * Custom hooks for API data fetching
 * Provides React hooks for managing API state and data fetching
 */

import { useState, useEffect, useCallback } from 'react';
import { apiClient, Train, Station, Disruption, KPIData } from '@/lib/api';

// Generic hook for API data fetching
function useApiData<T>(
  fetchFunction: () => Promise<T>,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await fetchFunction();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('API fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

// Specific hooks for different data types
export function useTrains(page: number = 1, limit: number = 10) {
  return useApiData(() => apiClient.getTrains(page, limit), [page, limit]);
}

export function useAllTrains() {
  return useApiData(() => apiClient.getAllTrains());
}

export function useActiveTrainsCount() {
  return useApiData(() => apiClient.getActiveTrainsCount());
}

export function useTrain(trainId: string) {
  return useApiData(() => apiClient.getTrain(trainId), [trainId]);
}

export function useCSVTrains() {
  return useApiData(() => apiClient.getCSVTrains());
}

export function useStations() {
  return useApiData(() => apiClient.getStations());
}

export function useDisruptions() {
  return useApiData(() => apiClient.getDisruptions());
}

export function useKPIData() {
  return useApiData(() => apiClient.getKPIData());
}

// Hook for real-time data updates
export function useRealtimeData(intervalMs: number = 30000) {
  const trains = useCSVTrains(); // Use CSV trains for real-time updates (100+ trains)
  const disruptions = useDisruptions();
  const kpiData = useKPIData();

  useEffect(() => {
    const interval = setInterval(() => {
      trains.refetch();
      disruptions.refetch();
      kpiData.refetch();
    }, intervalMs);

    return () => clearInterval(interval);
  }, [intervalMs, trains.refetch, disruptions.refetch, kpiData.refetch]);

  return {
    trains: trains.data || [],
    disruptions: disruptions.data || [],
    kpiData: kpiData.data,
    loading: trains.loading || disruptions.loading || kpiData.loading,
    error: trains.error || disruptions.error || kpiData.error,
  };
}

// Hook for optimization
export function useOptimization() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const optimize = useCallback(async (trains: Train[], constraints: Record<string, any> = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.optimizeSchedule({
        trains,
        constraints,
        objective: 'minimize_delays'
      });
      setResult(response);
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Optimization failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { optimize, loading, error, result };
}
