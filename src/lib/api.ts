// API client for microservices
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('admin_token', token);
      } else {
        localStorage.removeItem('admin_token');
      }
    }
  }

  getToken(): string | null {
    if (this.token) return this.token;
    if (typeof window !== 'undefined') {
      return localStorage.getItem('admin_token');
    }
    return null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    };

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Organizations (Chamas)
  async getOrganizations(params?: { status?: string; search?: string }) {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request<any[]>(`/admin/organizations${query ? `?${query}` : ''}`);
  }

  async getOrganization(id: string) {
    return this.request<any>(`/admin/organizations/${id}`);
  }

  async createOrganization(data: any) {
    return this.request<any>('/admin/organizations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateOrganization(id: string, data: any) {
    return this.request<any>(`/admin/organizations/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteOrganization(id: string) {
    return this.request<any>(`/admin/organizations/${id}`, {
      method: 'DELETE',
    });
  }

  async activateOrganization(id: string) {
    return this.request<any>(`/admin/organizations/${id}/activate`, {
      method: 'POST',
    });
  }

  async suspendOrganization(id: string) {
    return this.request<any>(`/admin/organizations/${id}/suspend`, {
      method: 'POST',
    });
  }

  // Members
  async getMembers(params?: { organization_id?: string; search?: string; role?: string }) {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request<any[]>(`/admin/members${query ? `?${query}` : ''}`);
  }

  async getMember(id: string) {
    return this.request<any>(`/admin/members/${id}`);
  }

  async updateMember(id: string, data: any) {
    return this.request<any>(`/admin/members/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async transferMember(id: string, new_organization_id: string) {
    return this.request<any>(`/admin/members/${id}/transfer`, {
      method: 'POST',
      body: JSON.stringify({ organization_id: new_organization_id }),
    });
  }

  // Contributions
  async getContributions(params?: { organization_id?: string; member_id?: string }) {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request<any[]>(`/admin/contributions${query ? `?${query}` : ''}`);
  }

  async createContribution(data: any) {
    return this.request<any>('/admin/contributions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Loans
  async getLoans(params?: { organization_id?: string; status?: string }) {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request<any[]>(`/admin/loans${query ? `?${query}` : ''}`);
  }

  async approveLoan(id: string) {
    return this.request<any>(`/admin/loans/${id}/approve`, {
      method: 'POST',
    });
  }

  // Proposals
  async getProposals(params?: { organization_id?: string; status?: string }) {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request<any[]>(`/admin/proposals${query ? `?${query}` : ''}`);
  }

  // Analytics
  async getDashboardStats() {
    return this.request<any>('/admin/analytics/overview');
  }

  async getRevenueStats(period: string = 'month') {
    return this.request<any>(`/admin/analytics/revenue?period=${period}`);
  }

  async getChamaGrowth() {
    return this.request<any[]>('/admin/analytics/chamas/growth');
  }

  // Settings
  async getPlatformSettings() {
    return this.request<any>('/admin/settings');
  }

  async updatePlatformSettings(data: any) {
    return this.request<any>('/admin/settings', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // Auth (for login - using mock for now)
  async login(email: string, password: string) {
    // Mock login - in production, this would call the auth service
    if (email && password) {
      const mockToken = 'mock_admin_token_' + Date.now();
      this.setToken(mockToken);
      return {
        token: mockToken,
        user: {
          id: 'admin_001',
          email,
          name: 'Super Admin',
          role: 'SUPER_ADMIN',
        },
      };
    }
    throw new Error('Invalid credentials');
  }

  async logout() {
    this.setToken(null);
  }
}

export const api = new ApiClient();
