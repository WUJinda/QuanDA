import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Layout from '@/layouts/MainLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'DataAnalysis' }
      },
      {
        path: 'market',
        name: 'Market',
        component: () => import('@/views/Market/index.vue'),
        meta: { title: '市场行情', icon: 'TrendCharts' }
      },
      {
        path: 'futures',
        name: 'Futures',
        component: () => import('@/views/Futures/index.vue'),
        meta: { title: '期货分析', icon: 'Histogram' }
      },
      {
        path: 'account',
        name: 'Account',
        component: () => import('@/views/Account/index.vue'),
        meta: { title: '账户管理', icon: 'Wallet' }
      },
      {
        path: 'backtest',
        name: 'Backtest',
        component: () => import('@/views/Backtest/index.vue'),
        meta: { title: '回测系统', icon: 'Operation' }
      },
      {
        path: 'strategy',
        name: 'Strategy',
        component: () => import('@/views/Strategy/index.vue'),
        meta: { title: '策略管理', icon: 'Document' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
