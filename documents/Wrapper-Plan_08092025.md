# Wrapper-Plan.md - ABM System Interface Design
**Version: 08-09-2025 16:20:00**  
**Authored by: Sotiris Spyrou, CEO, VerityAI**  
**File Path: //documents/Wrapper-Plan_08092025.md**

## 🎯 Interface Strategy Overview

### **Wrapper Approach Rationale**
The ABM Content Marketing Engine requires a sophisticated **multi-layer interface architecture** that wraps the core AI system prompts with user-friendly interfaces, real-time dashboards, and seamless integrations. The wrapper serves as the **orchestration layer** between human users and the intelligent automation engines.

### **Design Philosophy: Progressive Disclosure**
- **Layer 1**: Simple, actionable insights for daily operations
- **Layer 2**: Detailed analytics and configuration for power users  
- **Layer 3**: Advanced system administration and optimization
- **Layer 4**: Developer API access for custom integrations

## 🏗️ Wrapper Architecture Design

### **Component Hierarchy**
```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                 │
├─────────────────────────────────────────────────────────┤
│  Dashboard UI  │  Config UI  │  Analytics UI  │  Admin  │
├─────────────────────────────────────────────────────────┤
│                 API ABSTRACTION LAYER                   │
├─────────────────────────────────────────────────────────┤
│  REST API  │  GraphQL  │  WebSocket  │  Webhook Handler │
├─────────────────────────────────────────────────────────┤
│                   BUSINESS LOGIC LAYER                  │
├─────────────────────────────────────────────────────────┤
│ Content Engine │ Journey Engine │ Analytics │ Nurture   │
├─────────────────────────────────────────────────────────┤
│                  INTEGRATION LAYER                      │
├─────────────────────────────────────────────────────────┤
│   HubSpot API  │  Claude API   │  Supabase  │  External │
└─────────────────────────────────────────────────────────┘
```

### **Interface Design Principles**

#### **1. Simplicity Over Complexity**
Following Elon Musk's first principles:
- **Question Requirements**: Do users really need this feature?
- **Delete Unnecessary Steps**: Minimize clicks to actionable insights
- **Optimize & Simplify**: One-click actions for common tasks
- **Automate Everything**: Reduce manual intervention to zero where possible

#### **2. Real-Time Intelligence**
- **Live Data Streams**: WebSocket connections for instant updates
- **Contextual Notifications**: Smart alerts based on ABM signals
- **Predictive Insights**: Proactive recommendations before users ask
- **Instant Feedback**: Immediate response to user actions

#### **3. Mobile-First Responsive Design**
- **Progressive Web App**: Offline capability for core features
- **Touch Optimized**: Gesture-based navigation for mobile devices
- **Adaptive Layouts**: Context-aware interface adaptation
- **Fast Loading**: <2 second page load times on mobile networks

## 📱 User Interface Components

### **Primary Dashboard (Landing Interface)**

#### **Executive Summary Card**
```typescript
interface ExecutiveSummaryProps {
  accountsTracked: number;
  conversionRate: number;
  pipelineGenerated: number;
  trendDirection: 'up' | 'down' | 'stable';
}

const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({
  accountsTracked,
  conversionRate, 
  pipelineGenerated,
  trendDirection
}) => (
  <Card className="bg-gradient-to-br from-blue-600 to-purple-700 text-white">
    <CardHeader>
      <h2 className="text-2xl font-bold">ABM Performance Overview</h2>
    </CardHeader>
    <CardContent>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <MetricCard
          label="Accounts Tracked"
          value={accountsTracked}
          icon={<Building2 />}
        />
        <MetricCard
          label="Conversion Rate"
          value={`${conversionRate}%`}
          target={15}
          trend={trendDirection}
          icon={<TrendingUp />}
        />
        <MetricCard
          label="Pipeline Generated"
          value={formatCurrency(pipelineGenerated)}
          icon={<DollarSign />}
        />
      </div>
    </CardContent>
  </Card>
);
```

#### **Real-Time Activity Feed**
```typescript
interface ActivityFeedProps {
  activities: ABMActivity[];
  onActivityClick: (activity: ABMActivity) => void;
}

const ActivityFeed: React.FC<ActivityFeedProps> = ({ activities, onActivityClick }) => (
  <Card className="h-96 overflow-hidden">
    <CardHeader>
      <h3 className="text-lg font-semibold flex items-center">
        <Zap className="mr-2 text-yellow-500" />
        Live ABM Activity
      </h3>
    </CardHeader>
    <CardContent className="p-0">
      <ScrollArea className="h-80">
        {activities.map((activity) => (
          <ActivityItem
            key={activity.id}
            activity={activity}
            onClick={() => onActivityClick(activity)}
            className="hover:bg-gray-50 cursor-pointer transition-colors"
          />
        ))}
      </ScrollArea>
    </CardContent>
  </Card>
);
```

### **Account Intelligence Interface**

#### **Account Overview Widget**
```typescript
interface AccountOverviewProps {
  account: EnterpriseAccount;
  engagementScore: number;
  stakeholders: Contact[];
  journeyStage: JourneyStage;
  nextActions: RecommendedAction[];
}

const AccountOverview: React.FC<AccountOverviewProps> = ({
  account,
  engagementScore,
  stakeholders,
  journeyStage,
  nextActions
}) => (
  <div className="space-y-6">
    {/* Account Header */}
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <Avatar className="h-16 w-16">
          <AvatarImage src={account.logoUrl} alt={account.name} />
          <AvatarFallback>{account.name.substring(0, 2)}</AvatarFallback>
        </Avatar>
        <div>
          <h1 className="text-2xl font-bold">{account.name}</h1>
          <p className="text-gray-600">{account.industry} • {account.employeeCount} employees</p>
        </div>
      </div>
      <EngagementScoreBadge score={engagementScore} />
    </div>

    {/* Journey Stage Progression */}
    <JourneyStageTracker
      currentStage={journeyStage}
      progressData={account.journeyHistory}
    />

    {/* Stakeholder Map */}
    <StakeholderGrid
      stakeholders={stakeholders}
      onStakeholderSelect={(stakeholder) => handleStakeholderSelect(stakeholder)}
    />

    {/* Recommended Actions */}
    <RecommendedActionsPanel
      actions={nextActions}
      onActionExecute={(action) => executeAction(action)}
    />
  </div>
);
```

#### **Content Performance Heatmap**
```typescript
interface ContentHeatmapProps {
  contentPerformance: ContentMetrics[];
  timeRange: DateRange;
  onContentSelect: (contentId: string) => void;
}

const ContentHeatmap: React.FC<ContentHeatmapProps> = ({
  contentPerformance,
  timeRange,
  onContentSelect
}) => (
  <Card>
    <CardHeader>
      <h3 className="text-lg font-semibold">Content Engagement Heatmap</h3>
      <DateRangePicker value={timeRange} onChange={setTimeRange} />
    </CardHeader>
    <CardContent>
      <ResponsiveContainer width="100%" height={400}>
        <Treemap
          data={contentPerformance}
          dataKey="engagementScore"
          aspectRatio={4/3}
          stroke="#fff"
          fill="#3b82f6"
          onClick={(data) => onContentSelect(data.contentId)}
        >
          <Tooltip content={<ContentTooltip />} />
        </Treemap>
      </ResponsiveContainer>
    </CardContent>
  </Card>
);
```

### **Configuration Interface**

#### **Sequence Builder (Visual Flow)**
```typescript
interface SequenceBuilderProps {
  sequence: NurtureSequence;
  onSequenceUpdate: (sequence: NurtureSequence) => void;
}

const SequenceBuilder: React.FC<SequenceBuilderProps> = ({
  sequence,
  onSequenceUpdate
}) => {
  const [nodes, setNodes] = useState<Node[]>(sequenceToNodes(sequence));
  const [edges, setEdges] = useState<Edge[]>(sequenceToEdges(sequence));

  return (
    <div className="h-screen">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={(changes) => setNodes(applyNodeChanges(changes, nodes))}
        onEdgesChange={(changes) => setEdges(applyEdgeChanges(changes, edges))}
        nodeTypes={{
          trigger: TriggerNode,
          action: ActionNode,
          condition: ConditionNode,
          delay: DelayNode
        }}
        fitView
        className="bg-gray-50"
      >
        <Controls />
        <MiniMap />
        <Background />
        <Panel position="top-right">
          <SequenceControls
            sequence={sequence}
            onSave={() => saveSequence(nodesToSequence(nodes, edges))}
            onTest={() => testSequence(sequence)}
          />
        </Panel>
      </ReactFlow>
    </div>
  );
};
```

## 🔌 API Wrapper Design

### **RESTful API Abstraction**

#### **Unified Endpoint Structure**
```typescript
// Primary API Routes
const API_ROUTES = {
  // Account Management
  accounts: {
    list: '/api/v1/accounts',
    detail: '/api/v1/accounts/:id',
    analytics: '/api/v1/accounts/:id/analytics',
    stakeholders: '/api/v1/accounts/:id/stakeholders'
  },
  
  // Content Operations
  content: {
    recommend: '/api/v1/content/recommend',
    performance: '/api/v1/content/performance',
    library: '/api/v1/content/library'
  },
  
  // Engagement Tracking
  engagement: {
    events: '/api/v1/engagement/events',
    scores: '/api/v1/engagement/scores',
    analytics: '/api/v1/engagement/analytics'
  },
  
  // Sequence Management
  sequences: {
    library: '/api/v1/sequences',
    enroll: '/api/v1/sequences/enroll',
    performance: '/api/v1/sequences/:id/performance'
  }
};
```

#### **Smart API Client with Caching**
```typescript
class ABMApiClient {
  private cache = new Map<string, { data: any; timestamp: number }>();
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  async getAccountAnalytics(
    accountId: string, 
    options: { refresh?: boolean } = {}
  ): Promise<AccountAnalytics> {
    const cacheKey = `account-analytics-${accountId}`;
    
    if (!options.refresh) {
      const cached = this.getCachedData(cacheKey);
      if (cached) return cached;
    }

    const response = await this.fetch(`/api/v1/accounts/${accountId}/analytics`);
    const data = await response.json();
    
    this.setCachedData(cacheKey, data);
    return data;
  }

  async recommendContent(
    contactId: string,
    preferences: ContentPreferences
  ): Promise<ContentRecommendation[]> {
    // Real-time endpoint - no caching
    const response = await this.fetch('/api/v1/content/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ contactId, preferences })
    });

    return response.json();
  }

  private getCachedData(key: string): any | null {
    const cached = this.cache.get(key);
    if (!cached) return null;
    
    const isExpired = Date.now() - cached.timestamp > this.CACHE_DURATION;
    if (isExpired) {
      this.cache.delete(key);
      return null;
    }
    
    return cached.data;
  }
}
```

### **WebSocket Real-Time Updates**

#### **Event-Driven State Management**
```typescript
interface WebSocketManager {
  connect(): void;
  disconnect(): void;
  subscribe(channel: string, callback: (data: any) => void): void;
  unsubscribe(channel: string): void;
}

class ABMWebSocketManager implements WebSocketManager {
  private ws: WebSocket | null = null;
  private subscriptions = new Map<string, Set<(data: any) => void>>();

  connect(): void {
    this.ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL!);
    
    this.ws.onmessage = (event) => {
      const { channel, data } = JSON.parse(event.data);
      const callbacks = this.subscriptions.get(channel);
      
      callbacks?.forEach(callback => callback(data));
    };

    this.ws.onopen = () => {
      console.log('ABM WebSocket connected');
      // Resubscribe to all channels
      this.subscriptions.forEach((_, channel) => {
        this.send({ type: 'subscribe', channel });
      });
    };
  }

  subscribe(channel: string, callback: (data: any) => void): void {
    if (!this.subscriptions.has(channel)) {
      this.subscriptions.set(channel, new Set());
      this.send({ type: 'subscribe', channel });
    }
    
    this.subscriptions.get(channel)!.add(callback);
  }
}

// Usage in React components
const useRealTimeEngagement = (accountId: string) => {
  const [engagementEvents, setEngagementEvents] = useState<EngagementEvent[]>([]);
  
  useEffect(() => {
    const ws = new ABMWebSocketManager();
    ws.connect();
    
    ws.subscribe(`account-${accountId}-engagement`, (event: EngagementEvent) => {
      setEngagementEvents(prev => [event, ...prev.slice(0, 99)]); // Keep last 100
    });
    
    return () => ws.disconnect();
  }, [accountId]);
  
  return engagementEvents;
};
```

## 🎨 Design System & Component Library

### **Tailwind CSS Design Tokens**
```typescript
// theme/tokens.ts
export const designTokens = {
  colors: {
    primary: {
      50: '#eff6ff',
      500: '#3b82f6',
      700: '#1d4ed8',
      900: '#1e3a8a'
    },
    success: {
      50: '#f0fdf4',
      500: '#10b981',
      700: '#047857'
    },
    warning: {
      50: '#fffbeb',
      500: '#f59e0b',
      700: '#d97706'
    },
    danger: {
      50: '#fef2f2',
      500: '#ef4444',
      700: '#dc2626'
    }
  },
  spacing: {
    'card-padding': '1.5rem',
    'section-gap': '2rem',
    'component-gap': '1rem'
  },
  borderRadius: {
    'card': '0.75rem',
    'button': '0.5rem',
    'input': '0.375rem'
  },
  animation: {
    'fade-in': 'fadeIn 0.2s ease-in-out',
    'slide-up': 'slideUp 0.3s ease-out',
    'scale-in': 'scaleIn 0.2s ease-out'
  }
};
```

### **Reusable Component Architecture**
```typescript
// components/ui/MetricCard.tsx
interface MetricCardProps {
  label: string;
  value: string | number;
  target?: number;
  trend?: 'up' | 'down' | 'stable';
  icon?: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  target,
  trend,
  icon,
  className = '',
  onClick
}) => {
  const trendColor = {
    up: 'text-green-600',
    down: 'text-red-600',
    stable: 'text-gray-600'
  }[trend || 'stable'];

  const trendIcon = {
    up: <TrendingUp className="h-4 w-4" />,
    down: <TrendingDown className="h-4 w-4" />,
    stable: <Minus className="h-4 w-4" />
  }[trend || 'stable'];

  return (
    <Card 
      className={`p-4 hover:shadow-md transition-shadow cursor-pointer ${className}`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {icon}
          <span className="text-sm font-medium text-gray-600">{label}</span>
        </div>
        {trend && (
          <div className={`flex items-center space-x-1 ${trendColor}`}>
            {trendIcon}
          </div>
        )}
      </div>
      <div className="mt-2">
        <div className="text-2xl font-bold">{value}</div>
        {target && (
          <div className="text-sm text-gray-500">
            Target: {target}{typeof value === 'string' && value.includes('%') ? '%' : ''}
          </div>
        )}
      </div>
    </Card>
  );
};
```

## 🔄 State Management Strategy

### **Zustand Store Architecture**
```typescript
// stores/abmStore.ts
interface ABMStore {
  // State
  accounts: EnterpriseAccount[];
  selectedAccount: EnterpriseAccount | null;
  engagementEvents: EngagementEvent[];
  contentRecommendations: ContentRecommendation[];
  
  // Loading states
  loading: {
    accounts: boolean;
    recommendations: boolean;
    analytics: boolean;
  };
  
  // Actions
  fetchAccounts: () => Promise<void>;
  selectAccount: (accountId: string) => void;
  updateEngagementScore: (contactId: string, score: number) => void;
  enrollInSequence: (contactId: string, sequenceId: string) => Promise<void>;
}

export const useABMStore = create<ABMStore>((set, get) => ({
  accounts: [],
  selectedAccount: null,
  engagementEvents: [],
  contentRecommendations: [],
  
  loading: {
    accounts: false,
    recommendations: false,
    analytics: false
  },

  fetchAccounts: async () => {
    set(state => ({ loading: { ...state.loading, accounts: true } }));
    
    try {
      const accounts = await apiClient.getAccounts();
      set({ accounts });
    } catch (error) {
      console.error('Failed to fetch accounts:', error);
    } finally {
      set(state => ({ loading: { ...state.loading, accounts: false } }));
    }
  },

  selectAccount: (accountId: string) => {
    const account = get().accounts.find(a => a.id === accountId);
    set({ selectedAccount: account || null });
  },

  updateEngagementScore: (contactId: string, score: number) => {
    // Optimistic update
    set(state => ({
      engagementEvents: state.engagementEvents.map(event =>
        event.contactId === contactId
          ? { ...event, engagementScore: score }
          : event
      )
    }));
  }
}));
```

## 📱 Progressive Web App Features

### **Offline Capability**
```typescript
// lib/serviceWorker.ts
const CACHE_NAME = 'abm-dashboard-v1';
const OFFLINE_URLS = [
  '/',
  '/dashboard',
  '/accounts',
  '/analytics',
  '/offline'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(OFFLINE_URLS))
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/api/')) {
    // Handle API requests with network-first strategy
    event.respondWith(
      fetch(event.request)
        .catch(() => caches.match('/offline-data.json'))
    );
  } else {
    // Handle static assets with cache-first strategy
    event.respondWith(
      caches.match(event.request)
        .then(response => response || fetch(event.request))
    );
  }
});
```

### **Push Notifications**
```typescript
// lib/notifications.ts
export class ABMNotificationManager {
  async requestPermission(): Promise<boolean> {
    if (!('Notification' in window)) return false;
    
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }

  async showEngagementAlert(contact: Contact, event: EngagementEvent): Promise<void> {
    if (!this.hasPermission()) return;

    new Notification(`High Engagement Alert`, {
      body: `${contact.firstName} ${contact.lastName} from ${contact.company} showed strong interest`,
      icon: '/icons/engagement-alert.png',
      tag: `engagement-${contact.id}`,
      requireInteraction: true,
      actions: [
        { action: 'view', title: 'View Account' },
        { action: 'dismiss', title: 'Dismiss' }
      ]
    });
  }

  private hasPermission(): boolean {
    return 'Notification' in window && Notification.permission === 'granted';
  }
}
```

## 🧪 Testing Strategy for Interface

### **Component Testing with React Testing Library**
```typescript
// tests/components/MetricCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { MetricCard } from '@/components/ui/MetricCard';

describe('MetricCard', () => {
  it('displays metric value and label correctly', () => {
    render(
      <MetricCard
        label="Conversion Rate"
        value="15.3%"
        target={15}
        trend="up"
      />
    );

    expect(screen.getByText('Conversion Rate')).toBeInTheDocument();
    expect(screen.getByText('15.3%')).toBeInTheDocument();
    expect(screen.getByText('Target: 15%')).toBeInTheDocument();
  });

  it('handles click events correctly', () => {
    const handleClick = jest.fn();
    render(
      <MetricCard
        label="Test Metric"
        value={100}
        onClick={handleClick}
      />
    );

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### **Integration Testing with Playwright**
```typescript
// tests/e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test.describe('ABM Dashboard', () => {
  test('should display account overview with real-time updates', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Verify dashboard loads
    await expect(page.locator('h1')).toContainText('ABM Performance Overview');
    
    // Verify metrics are displayed
    await expect(page.locator('[data-testid="accounts-tracked"]')).toBeVisible();
    await expect(page.locator('[data-testid="conversion-rate"]')).toBeVisible();
    
    // Test real-time updates
    await page.waitForSelector('[data-testid="activity-feed"]');
    const initialActivities = await page.locator('[data-testid="activity-item"]').count();
    
    // Simulate new activity (would come from WebSocket in real scenario)
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('new-engagement', {
        detail: { contactId: 'test-123', eventType: 'content_download' }
      }));
    });
    
    // Verify activity feed updated
    await expect(page.locator('[data-testid="activity-item"]')).toHaveCount(initialActivities + 1);
  });
});
```

## 🚀 Deployment & Infrastructure

### **Next.js + Vercel Deployment Configuration**
```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  images: {
    domains: ['avatars.githubusercontent.com', 'hubspot.com'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.API_BASE_URL + '/:path*',
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
```

### **Docker Configuration for Local Development**
```dockerfile
# Dockerfile
FROM node:18-alpine AS base
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Build application
COPY . .
RUN npm run build

# Production image
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=base /app/public ./public
COPY --from=base /app/.next/standalone ./
COPY --from=base /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
```

---

**This wrapper plan provides a comprehensive interface strategy that transforms the intelligent ABM engines into an intuitive, powerful user experience optimized for enterprise B2B marketing teams.**
