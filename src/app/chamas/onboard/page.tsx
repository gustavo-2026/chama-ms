'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input, Textarea, Select } from '@/components/ui/input';
import { Building2, ArrowLeft, ArrowRight, Check } from 'lucide-react';
import Link from 'next/link';

const regions = [
  'Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 
  'Kakamega', 'Kericho', 'Meru', 'Thika', 'Malindi'
];

const subscriptionTiers = [
  { id: 'free', name: 'Free', price: 0, features: ['Up to 30 members', 'Basic features'] },
  { id: 'pro', name: 'Pro', price: 2990, features: ['Up to 100 members', 'Marketplace', 'Advanced analytics'] },
  { id: 'enterprise', name: 'Enterprise', price: 9990, features: ['Unlimited members', 'All features', 'Priority support'] },
];

export default function OnboardChamaPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    // Step 1: Basic Info
    name: '',
    code: '',
    region: '',
    description: '',
    // Step 2: Subscription
    tier: 'free',
    // Step 3: Chair Info
    chair_name: '',
    chair_email: '',
    chair_phone: '',
  });

  const handleSubmit = async () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      router.push('/chamas');
    }, 1500);
  };

  const updateField = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <DashboardLayout>
      <Header title="Onboard New Chama" subtitle="Create a new chama on the platform" />

      <div className="p-6 max-w-4xl mx-auto">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex items-center">
                <div
                  className={`h-10 w-10 rounded-full flex items-center justify-center font-medium ${
                    step >= s
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {step > s ? <Check className="h-5 w-5" /> : s}
                </div>
                {s < 3 && (
                  <div
                    className={`h-1 w-20 mx-2 ${
                      step > s ? 'bg-primary-600' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-2">
            <span className="text-sm text-gray-500">Basic Info</span>
            <span className="text-sm text-gray-500">Subscription</span>
            <span className="text-sm text-gray-500">Admin Details</span>
          </div>
        </div>

        {/* Step 1: Basic Info */}
        {step === 1 && (
          <Card>
            <CardHeader>
              <CardTitle>Chama Information</CardTitle>
              <CardDescription>
                Enter the basic details about the chama
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Chama Name *
                </label>
                <Input
                  placeholder="e.g., Mwanzo Group"
                  value={formData.name}
                  onChange={(e) => updateField('name', e.target.value)}
                  className="mt-1"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Chama Code *
                  </label>
                  <Input
                    placeholder="e.g., MWANZO"
                    value={formData.code}
                    onChange={(e) => updateField('code', e.target.value.toUpperCase())}
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Region *
                  </label>
                  <select
                    className="mt-1 flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm"
                    value={formData.region}
                    onChange={(e) => updateField('region', e.target.value)}
                  >
                    <option value="">Select region</option>
                    {regions.map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Description
                </label>
                <Textarea
                  placeholder="Brief description of the chama..."
                  value={formData.description}
                  onChange={(e) => updateField('description', e.target.value)}
                  className="mt-1"
                />
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Subscription */}
        {step === 2 && (
          <Card>
            <CardHeader>
              <CardTitle>Choose Subscription</CardTitle>
              <CardDescription>
                Select the plan that best fits your needs
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                {subscriptionTiers.map((tier) => (
                  <div
                    key={tier.id}
                    className={`border rounded-lg p-4 cursor-pointer transition-all ${
                      formData.tier === tier.id
                        ? 'border-primary-600 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => updateField('tier', tier.id)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold">{tier.name}</h3>
                      {formData.tier === tier.id && (
                        <Check className="h-5 w-5 text-primary-600" />
                      )}
                    </div>
                    <p className="text-2xl font-bold mb-4">
                      KES {tier.price.toLocaleString()}
                      <span className="text-sm font-normal text-gray-500">/mo</span>
                    </p>
                    <ul className="space-y-2">
                      {tier.features.map((feature, i) => (
                        <li key={i} className="text-sm text-gray-600 flex items-center gap-2">
                          <Check className="h-4 w-4 text-green-500" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Chair Info */}
        {step === 3 && (
          <Card>
            <CardHeader>
              <CardTitle>Chairperson Details</CardTitle>
              <CardDescription>
                Add the primary admin for this chama
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Full Name *
                </label>
                <Input
                  placeholder="e.g., John Doe"
                  value={formData.chair_name}
                  onChange={(e) => updateField('chair_name', e.target.value)}
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Email *
                </label>
                <Input
                  type="email"
                  placeholder="e.g., john@chama.co.ke"
                  value={formData.chair_email}
                  onChange={(e) => updateField('chair_email', e.target.value)}
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Phone Number *
                </label>
                <Input
                  placeholder="e.g., 254712345678"
                  value={formData.chair_phone}
                  onChange={(e) => updateField('chair_phone', e.target.value)}
                  className="mt-1"
                />
              </div>
            </CardContent>
          </Card>
        )}

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-6">
          {step > 1 ? (
            <Button variant="outline" onClick={() => setStep(step - 1)}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
          ) : (
            <Link href="/chamas">
              <Button variant="outline">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Cancel
              </Button>
            </Link>
          )}

          {step < 3 ? (
            <Button onClick={() => setStep(step + 1)}>
              Next
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={loading}>
              {loading ? 'Creating...' : 'Create Chama'}
              <Check className="ml-2 h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
