/**
 * API Client for RailOptima Backend
 * Handles all API communications with the FastAPI backend
 */

// Use relative URLs for same-domain deployment
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api'  // Same domain in production
  : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'); // Direct backend in development

export interface Train {
  id: string;
  name: string;
  route: string;
  departure_time: string;
  arrival_time: string;
  status: string;
  priority: number;
  capacity: number;
  current_station?: string;
  delay_minutes: number;
}

export interface Station {
  id: string;
  name: string;
  location: { lat: number; lng: number };
  capacity: number;
  current_trains: number;
  status: string;
}

export interface Disruption {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  affected_trains: string[];
  affected_stations: string[];
  start_time: string;
  estimated_end_time?: string;
  description: string;
}

export interface KPIData {
  punctuality: { value: number; target: number; trend: number };
  avgDelay: { value: number; target: number; trend: number };
  activeTrains: { value: number; capacity: number; trend: number };
  disruptions: { value: number; last24h: number; trend: number };
}

export interface OptimizationRequest {
  trains: Train[];
  constraints: Record<string, any>;
  objective: string;
}

export interface OptimizationResponse {
  optimized_trains: Train[];
  conflicts_resolved: number;
  total_delay_reduction: number;
  optimization_time: number;
  status: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  async getCSVTrains(): Promise<Train[]> {
    return this.request('/trains/csv');
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string; uptime: string }> {
    return this.request('/health');
  }

  // Train endpoints
  async getTrains(page: number = 1, limit: number = 10): Promise<{ trains: Train[]; pagination: any }> {
    return this.request(`/trains?page=${page}&limit=${limit}`);
  }

  async getAllTrains(): Promise<Train[]> {
    return this.request('/trains');
  }

  async getActiveTrainsCount(): Promise<{ total_active_trains: number; timestamp: string }> {
    return this.request('/trains/count');
  }

  async getTrain(trainId: string): Promise<Train> {
    return this.request(`/trains/${trainId}`);
  }

  // Station endpoints
  async getStations(): Promise<Station[]> {
    return this.request('/stations');
  }

  // Disruption endpoints
  async getDisruptions(): Promise<Disruption[]> {
    return this.request('/disruptions');
  }

  async createDisruption(disruption: Omit<Disruption, 'id'>): Promise<Disruption> {
    return this.request('/disruptions', {
      method: 'POST',
      body: JSON.stringify(disruption),
    });
  }

  // KPI endpoints
  async getKPIData(): Promise<KPIData> {
    return this.request('/kpi');
  }

  // Optimization endpoints
  async optimizeSchedule(request: OptimizationRequest): Promise<OptimizationResponse> {
    return this.request('/optimize', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }
}

// Create and export a singleton instance
export const apiClient = new ApiClient();

// Export the class for testing or custom instances
export { ApiClient };
