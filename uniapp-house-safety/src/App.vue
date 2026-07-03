<script setup>
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { checkLoginStatus } from '@/utils/auth.js'

onLaunch(() => {
  console.log('App Launch')
  // 检查登录状态
  checkLoginStatus()
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style>
/* ========== Design Tokens — 与 client 工程蓝主题一致 ========== */
page {
  --color-primary: #226CB3;
  --color-primary-foreground: #ffffff;
  --color-primary-active: #1B5A96;
  --color-secondary: #EDF0F4;
  --color-secondary-foreground: #171D26;
  --color-success: #2EA65E;
  --color-success-foreground: #EBF5EE;
  --color-warning: #E28A13;
  --color-warning-foreground: #FBF0E0;
  --color-destructive: #D43535;
  --color-destructive-foreground: #FAEAEA;
  --color-muted: #EDF0F4;
  --color-muted-foreground: #626F7D;
  --color-accent: #F2F5F9;
  --color-accent-foreground: #171D26;
  --color-background: #F5F7FA;
  --color-card: #ffffff;
  --color-card-foreground: #171D26;
  --color-border: #DBDFE4;
  --color-input: #DBDFE4;
  --color-ring: #226CB3;
  --color-info-bg: #E8F0F8;
  --color-info-text: #226CB3;
  --color-success-bg: #EBF5EE;
  --color-warning-bg: #FBF0E0;
  --color-destructive-bg: #FAEAEA;

  /* Text hierarchy */
  --text-heading: #171D26;
  --text-body: #454D59;
  --text-secondary: #626F7D;
  --text-hint: #B0B8C2;

  /* Design constants — sharp engineering style */
  --radius-sm: 2rpx;
  --radius-md: 4rpx;
  --radius-lg: 6rpx;
  --radius-xl: 8rpx;
  --shadow-card: 0 2rpx 12rpx rgba(0, 0, 0, 0.02);
  --shadow-elevated: 0 2rpx 12rpx rgba(0, 0, 0, 0.03);
  --font-sans: 'Inter', 'PingFang SC', -apple-system, BlinkMacSystemFont, system-ui, 'Helvetica Neue', 'Microsoft Yahei', Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji';

  background-color: var(--color-background);
  font-family: var(--font-sans);
  color: var(--text-body);
  font-size: 28rpx;
  line-height: 1.6;
}

/* ========== Layout Utilities ========== */
.container {
  padding: 24rpx;
}

.card {
  background-color: var(--color-card);
  border-radius: var(--radius-md);
  padding: 24rpx;
  margin-bottom: 24rpx;
  box-shadow: var(--shadow-card);
}

/* ========== Button Utilities ========== */
.btn-primary {
  background-color: var(--color-primary);
  color: var(--color-primary-foreground);
  border: none;
  border-radius: var(--radius-sm);
  padding: 20rpx 40rpx;
  font-size: 28rpx;
}

.btn-primary:active {
  background-color: var(--color-primary-active);
}

.btn-secondary {
  background-color: var(--color-secondary);
  color: var(--color-secondary-foreground);
  border: none;
  border-radius: var(--radius-sm);
  padding: 20rpx 40rpx;
  font-size: 28rpx;
}

.btn-danger {
  background-color: var(--color-destructive);
  color: var(--color-primary-foreground);
  border: none;
  border-radius: var(--radius-sm);
  padding: 20rpx 40rpx;
  font-size: 28rpx;
}

/* ========== Text Utilities ========== */
.text-primary { color: var(--color-primary); }
.text-success { color: var(--color-success); }
.text-warning { color: var(--color-warning); }
.text-danger { color: var(--color-destructive); }
.text-heading { color: var(--text-heading); }
.text-body { color: var(--text-body); }
.text-secondary { color: var(--text-secondary); }
.text-hint { color: var(--text-hint); }

/* ========== Background Utilities ========== */
.bg-info { background-color: var(--color-info-bg); }
.bg-success { background-color: var(--color-success-bg); }
.bg-warning { background-color: var(--color-warning-bg); }
.bg-danger { background-color: var(--color-destructive-bg); }
.bg-muted { background-color: var(--color-muted); }

/* ========== Flex Utilities ========== */
.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* ========== Separator ========== */
.separator {
  border-top: 1rpx solid var(--color-border);
  margin: 16rpx 0;
}
</style>
