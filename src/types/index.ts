// Types for the Admin Console

export interface Organization {
  id: string;
  name: string;
  code: string;
  region: string;
  status: 'ACTIVE' | 'SUSPENDED' | 'PENDING';
  created_at: string;
  updated_at?: string;
}

export interface Member {
  id: string;
  name: string;
  email: string;
  phone: string;
  organization_id: string;
  organization_name?: string;
  role: 'CHAIR' | 'SECRETARY' | 'TREASURER' | 'MEMBER';
  status: 'ACTIVE' | 'SUSPENDED';
  created_at: string;
}

export interface Contribution {
  id: string;
  member_id: string;
  member_name?: string;
  amount: number;
  method: 'CASH' | 'MPESA' | 'BANK';
  status: 'PENDING' | 'COMPLETED' | 'FAILED';
  created_at: string;
}

export interface Loan {
  id: string;
  member_id: string;
  member_name?: string;
  principal_amount: number;
  interest_rate: number;
  term_months: number;
  monthly_payment: number;
  status: 'PENDING' | 'APPROVED' | 'ACTIVE' | 'REJECTED' | 'COMPLETED';
  created_at: string;
}

export interface Proposal {
  id: string;
  organization_id: string;
  organization_name?: string;
  title: string;
  description: string;
  proposed_by: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  votes_for: number;
  votes_against: number;
  created_at: string;
}

export interface Transaction {
  id: string;
  type: 'CONTRIBUTION' | 'LOAN_DISBURSEMENT' | 'LOAN_REPAYMENT' | 'EXPENSE';
  amount: number;
  status: 'PENDING' | 'COMPLETED' | 'FAILED';
  member_id: string;
  member_name?: string;
  organization_id: string;
  organization_name?: string;
  created_at: string;
}

export interface DashboardStats {
  total_chamas: number;
  active_chamas: number;
  total_members: number;
  total_contributions: number;
  total_loans: number;
  platform_revenue: number;
}

export interface AuditLog {
  id: string;
  action: string;
  user_id: string;
  user_name?: string;
  details: string;
  ip_address: string;
  created_at: string;
}

export interface PlatformSettings {
  platform_fee_percent: number;
  minimum_platform_fee: number;
  marketplace_enabled: boolean;
  loans_enabled: boolean;
  subscriptions_enabled: boolean;
  mpesa_configured: boolean;
  pesapal_configured: boolean;
}

export interface ChamaOnboardingData {
  name: string;
  code: string;
  region: string;
  subscription_tier: 'free' | 'pro' | 'enterprise';
  chair_name: string;
  chair_email: string;
  chair_phone: string;
}
