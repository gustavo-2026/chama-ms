'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input, Textarea } from '@/components/ui/input';
import { Settings, CreditCard, DollarSign, Shield, Bell, Palette, Save } from 'lucide-react';

const tabs = [
  { id: 'general', name: 'General', icon: Settings },
  { id: 'fees', name: 'Fees', icon: DollarSign },
  { id: 'payments', name: 'Payments', icon: CreditCard },
  { id: 'security', name: 'Security', icon: Shield },
];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('general');
  const [saving, setSaving] = useState(false);

  const [settings, setSettings] = useState({
    platformName: 'Chama Platform',
    supportEmail: 'support@chama.co.ke',
    platformFee: '2.0',
    minTransactionFee: '10',
    marketplaceEnabled: true,
    loansEnabled: true,
    subscriptionsEnabled: true,
  });

  const handleSave = () => {
    setSaving(true);
    setTimeout(() => setSaving(false), 1000);
  };

  return (
    <DashboardLayout>
      <Header title="Settings" subtitle="Configure platform settings" />

      <div className="p-6">
        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.name}
            </button>
          ))}
        </div>

        {/* General Settings */}
        {activeTab === 'general' && (
          <Card>
            <CardHeader>
              <CardTitle>General Settings</CardTitle>
              <CardDescription>Configure basic platform information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Platform Name</label>
                <Input
                  value={settings.platformName}
                  onChange={(e) => setSettings({ ...settings, platformName: e.target.value })}
                  className="mt-1 max-w-md"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Support Email</label>
                <Input
                  type="email"
                  value={settings.supportEmail}
                  onChange={(e) => setSettings({ ...settings, supportEmail: e.target.value })}
                  className="mt-1 max-w-md"
                />
              </div>
              <Button onClick={handleSave} disabled={saving}>
                <Save className="mr-2 h-4 w-4" />
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Fees Settings */}
        {activeTab === 'fees' && (
          <Card>
            <CardHeader>
              <CardTitle>Fee Configuration</CardTitle>
              <CardDescription>Set platform fees and charges</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Platform Fee (%)</label>
                <Input
                  type="number"
                  step="0.1"
                  value={settings.platformFee}
                  onChange={(e) => setSettings({ ...settings, platformFee: e.target.value })}
                  className="mt-1 max-w-md"
                />
                <p className="text-sm text-gray-500 mt-1">Fee charged on marketplace transactions</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Minimum Transaction Fee (KES)</label>
                <Input
                  type="number"
                  value={settings.minTransactionFee}
                  onChange={(e) => setSettings({ ...settings, minTransactionFee: e.target.value })}
                  className="mt-1 max-w-md"
                />
                <p className="text-sm text-gray-500 mt-1">Minimum fee per transaction</p>
              </div>
              <Button onClick={handleSave} disabled={saving}>
                <Save className="mr-2 h-4 w-4" />
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Payments Settings */}
        {activeTab === 'payments' && (
          <Card>
            <CardHeader>
              <CardTitle>Payment Configuration</CardTitle>
              <CardDescription>Configure M-Pesa and other payment methods</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">M-Pesa</h4>
                    <p className="text-sm text-gray-500">Mobile money payments</p>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Configured
                  </span>
                </div>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Pesapal</h4>
                    <p className="text-sm text-gray-500">Cards and bank transfers</p>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    Not Configured
                  </span>
                </div>
              </div>
              <Button onClick={handleSave} disabled={saving}>
                <Save className="mr-2 h-4 w-4" />
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Security Settings */}
        {activeTab === 'security' && (
          <Card>
            <CardHeader>
              <CardTitle>Security & Features</CardTitle>
              <CardDescription>Enable or disable platform features</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-medium">Marketplace</h4>
                  <p className="text-sm text-gray-500">Enable marketplace functionality</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.marketplaceEnabled}
                  onChange={(e) => setSettings({ ...settings, marketplaceEnabled: e.target.checked })}
                  className="h-5 w-5"
                />
              </div>
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-medium">Loans</h4>
                  <p className="text-sm text-gray-500">Enable loan features for chamas</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.loansEnabled}
                  onChange={(e) => setSettings({ ...settings, loansEnabled: e.target.checked })}
                  className="h-5 w-5"
                />
              </div>
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-medium">Subscriptions</h4>
                  <p className="text-sm text-gray-500">Enable paid subscription tiers</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.subscriptionsEnabled}
                  onChange={(e) => setSettings({ ...settings, subscriptionsEnabled: e.target.checked })}
                  className="h-5 w-5"
                />
              </div>
              <Button onClick={handleSave} disabled={saving}>
                <Save className="mr-2 h-4 w-4" />
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
