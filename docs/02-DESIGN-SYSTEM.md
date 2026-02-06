# 硬件助手 - UI/UX 设计系统

> Design System for Hardware Assistant

**文档版本**：v1.0.0  
**创建日期**：2026-02-06  
**最后更新**：2026-02-06  
**设计负责人**：硬件助手开发团队

---

## 1. 设计原则

### 1.1 核心设计理念
1. **简洁直观**：界面设计简洁，功能一目了然
2. **专业可信**：设计风格专业，数据展示准确
3. **高效便捷**：交互流畅，快速完成任务
4. **一致性强**：界面元素统一，降低学习成本

### 1.2 设计目标
- **易用性**：新用户 30 秒内理解核心功能
- **美观性**：界面美观，符合现代审美
- **响应性**：界面响应迅速，动画流畅
- **可访问性**：支持不同屏幕尺寸和系统设置

---

## 2. 色彩系统

### 2.1 主色调（Primary Colors）

#### 品牌主色
```scss
// 主品牌色 - 科技蓝
$primary-color: #007AFF;
$primary-light: #4DA3FF;
$primary-dark: #0051D5;
```

**使用场景**：
- 主要按钮
- 重要操作提示
- 选中状态
- 链接文字

#### 辅助色
```scss
// 成功色 - 绿色
$success-color: #52C41A;

// 警告色 - 橙色
$warning-color: #FAAD14;

// 错误色 - 红色
$error-color: #FF4D4F;

// 信息色 - 浅蓝
$info-color: #1890FF;
```

### 2.2 中性色（Neutral Colors）

```scss
// 文字颜色
$text-primary: #333333;    // 主要文字
$text-secondary: #666666;  // 次要文字
$text-tertiary: #999999;   // 辅助文字
$text-disabled: #CCCCCC;   // 禁用文字

// 背景颜色
$bg-page: #F5F5F5;         // 页面背景
$bg-card: #FFFFFF;         // 卡片背景
$bg-hover: #F0F0F0;        // 悬停背景

// 边框颜色
$border-light: #F0F0F0;    // 浅边框
$border-base: #D9D9D9;     // 基础边框
$border-dark: #999999;     // 深边框
```

### 2.3 品牌色（Brand Colors）

为不同硬件品牌定义专属主题色：

```scss
// CPU 品牌
$brand-intel: #0071C5;     // Intel 蓝
$brand-amd: #ED1C24;       // AMD 红

// GPU 品牌
$brand-nvidia: #76B900;    // NVIDIA 绿
$brand-amd-gpu: #ED1C24;   // AMD 红

// 手机品牌
$brand-apple: #000000;     // Apple 黑
$brand-xiaomi: #FF6700;    // 小米橙
$brand-huawei: #C8102E;    // 华为红
$brand-samsung: #1428A0;   // 三星蓝
```

### 2.4 渐变色（Gradient Colors）

```scss
// 页面标题背景渐变
$gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
$gradient-success: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
$gradient-warning: linear-gradient(135deg, #faad14 0%, #d48806 100%);

// 性能排行榜渐变
$gradient-gold: linear-gradient(135deg, #ffd700, #ffed4e);
$gradient-silver: linear-gradient(135deg, #c0c0c0, #e8e8e8);
$gradient-bronze: linear-gradient(135deg, #cd7f32, #e39d5f);

// 硬件类型渐变
$gradient-cpu: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
$gradient-gpu: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
$gradient-phone: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
```

---

## 3. 字体系统

### 3.1 字体家族

```scss
// 系统字体栈
$font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 
                   'Helvetica Neue', Arial, sans-serif;

// 数字字体（用于参数展示）
$font-family-number: 'DIN Alternate', 'Helvetica Neue', Arial, sans-serif;

// 代码字体（用于技术参数）
$font-family-code: 'SF Mono', 'Monaco', 'Consolas', monospace;
```

### 3.2 字体大小

```scss
// 标题字号
$font-size-h1: 40rpx;   // 一级标题
$font-size-h2: 36rpx;   // 二级标题
$font-size-h3: 32rpx;   // 三级标题
$font-size-h4: 28rpx;   // 四级标题

// 正文字号
$font-size-base: 28rpx;      // 基础字号
$font-size-large: 32rpx;     // 大号字体
$font-size-small: 24rpx;     // 小号字体
$font-size-mini: 20rpx;      // 迷你字体

// 特殊字号
$font-size-display: 48rpx;   // 展示字号（性能评分）
$font-size-caption: 22rpx;   // 说明文字
```

### 3.3 字重（Font Weight）

```scss
$font-weight-light: 300;    // 细体
$font-weight-normal: 400;   // 常规
$font-weight-medium: 500;   // 中等
$font-weight-bold: 600;     // 粗体
$font-weight-heavy: 700;    // 重磅
```

### 3.4 行高（Line Height）

```scss
$line-height-tight: 1.2;    // 紧凑（标题）
$line-height-base: 1.5;     // 基础（正文）
$line-height-loose: 1.8;    // 宽松（段落）
```

---

## 4. 间距系统

### 4.1 间距规范

采用 8rpx 基准间距系统：

```scss
$spacing-base: 8rpx;

// 间距变量
$spacing-xs: 8rpx;     // 超小间距
$spacing-sm: 16rpx;    // 小间距
$spacing-md: 24rpx;    // 中等间距
$spacing-lg: 32rpx;    // 大间距
$spacing-xl: 40rpx;    // 超大间距
$spacing-xxl: 48rpx;   // 特大间距
```

### 4.2 组件内边距（Padding）

```scss
// 按钮内边距
$button-padding-sm: 12rpx 24rpx;
$button-padding-md: 16rpx 32rpx;
$button-padding-lg: 20rpx 40rpx;

// 卡片内边距
$card-padding: 30rpx;

// 列表项内边距
$list-item-padding: 24rpx 30rpx;
```

### 4.3 组件外边距（Margin）

```scss
// 页面边距
$page-margin: 30rpx;

// 卡片间距
$card-margin: 20rpx;

// 列表间距
$list-margin: 16rpx;
```

---

## 5. 圆角系统

```scss
// 圆角半径
$border-radius-sm: 8rpx;     // 小圆角（标签）
$border-radius-base: 16rpx;  // 基础圆角（卡片）
$border-radius-lg: 20rpx;    // 大圆角（特殊卡片）
$border-radius-xl: 24rpx;    // 超大圆角
$border-radius-round: 100rpx; // 全圆角（按钮）
$border-radius-circle: 50%;   // 圆形
```

**使用场景**：
- **小圆角**：标签、徽章
- **基础圆角**：卡片、输入框
- **大圆角**：模态框、特殊卡片
- **全圆角**：按钮、搜索框
- **圆形**：头像、图标

---

## 6. 阴影系统

```scss
// 阴影效果
$shadow-sm: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);     // 轻微阴影
$shadow-base: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);  // 基础阴影
$shadow-lg: 0 8rpx 24rpx rgba(0, 0, 0, 0.12);    // 较大阴影
$shadow-xl: 0 12rpx 32rpx rgba(0, 0, 0, 0.15);   // 超大阴影
```

**使用场景**：
- **轻微阴影**：列表项悬停
- **基础阴影**：卡片默认状态
- **较大阴影**：卡片悬停、模态框
- **超大阴影**：抽屉、底部弹窗

---

## 7. 组件设计规范

### 7.1 按钮（Button）

#### 主按钮（Primary Button）
```scss
.button-primary {
  background: $primary-color;
  color: #FFFFFF;
  border-radius: $border-radius-round;
  padding: $button-padding-md;
  font-size: $font-size-base;
  font-weight: $font-weight-medium;
  
  &:active {
    background: $primary-dark;
  }
}
```

#### 次按钮（Secondary Button）
```scss
.button-secondary {
  background: transparent;
  color: $primary-color;
  border: 2rpx solid $primary-color;
  border-radius: $border-radius-round;
  padding: $button-padding-md;
  
  &:active {
    background: rgba(0, 122, 255, 0.05);
  }
}
```

### 7.2 卡片（Card）

#### 硬件卡片
```scss
.hardware-card {
  background: $bg-card;
  border-radius: $border-radius-base;
  padding: $card-padding;
  box-shadow: $shadow-base;
  
  &:active {
    transform: translateY(-2rpx);
    box-shadow: $shadow-lg;
  }
}
```

### 7.3 标签（Tag）

#### 品牌标签
```scss
.brand-tag {
  display: inline-block;
  padding: 6rpx 12rpx;
  border-radius: $border-radius-sm;
  font-size: $font-size-small;
  font-weight: $font-weight-medium;
  
  // Intel 品牌
  &.brand-intel {
    background: rgba(0, 113, 197, 0.1);
    color: $brand-intel;
  }
  
  // AMD 品牌
  &.brand-amd {
    background: rgba(237, 28, 36, 0.1);
    color: $brand-amd;
  }
}
```

### 7.4 徽章（Badge）

#### 性能评分徽章
```scss
.score-badge {
  display: inline-flex;
  align-items: baseline;
  padding: 8rpx 16rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: $border-radius-round;
  color: #FFFFFF;
  
  .score-text {
    font-size: $font-size-display;
    font-weight: $font-weight-bold;
    font-family: $font-family-number;
  }
  
  .score-label {
    font-size: $font-size-small;
    margin-left: 4rpx;
  }
}
```

### 7.5 列表项（List Item）

```scss
.list-item {
  background: $bg-card;
  padding: $list-item-padding;
  border-bottom: 1rpx solid $border-light;
  
  &:active {
    background: $bg-hover;
  }
  
  &:last-child {
    border-bottom: none;
  }
}
```

---

## 8. 图标系统

### 8.1 图标规范
- **尺寸**：24rpx、32rpx、40rpx、48rpx
- **颜色**：使用主题色或中性色
- **风格**：线性图标，统一粗细（2rpx）
- **来源**：优先使用 wot-design-uni 组件库图标

### 8.2 图标用途
| 图标类型 | 尺寸 | 使用场景 |
|---------|------|----------|
| 小图标 | 24rpx | 列表项、标签 |
| 中图标 | 32rpx | 按钮、输入框 |
| 大图标 | 40rpx | 卡片、导航 |
| 特大图标 | 48rpx | 空状态、引导页 |

---

## 9. 动画效果

### 9.1 过渡时间

```scss
// 动画时长
$transition-fast: 0.15s;     // 快速（按钮点击）
$transition-base: 0.3s;      // 基础（页面切换）
$transition-slow: 0.5s;      // 慢速（抽屉展开）
```

### 9.2 缓动函数

```scss
// 缓动曲线
$ease-in: cubic-bezier(0.4, 0, 1, 1);
$ease-out: cubic-bezier(0, 0, 0.2, 1);
$ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

### 9.3 常用动画

#### 淡入淡出
```scss
.fade-enter-active, .fade-leave-active {
  transition: opacity $transition-base $ease-in-out;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
```

#### 滑动
```scss
.slide-up-enter-active, .slide-up-leave-active {
  transition: transform $transition-base $ease-out;
}
.slide-up-enter-from {
  transform: translateY(100%);
}
.slide-up-leave-to {
  transform: translateY(-100%);
}
```

---

## 10. 响应式设计

### 10.1 断点系统

```scss
// 屏幕断点
$breakpoint-xs: 320px;   // 超小屏（iPhone SE）
$breakpoint-sm: 375px;   // 小屏（iPhone 8）
$breakpoint-md: 414px;   // 中屏（iPhone 11 Pro Max）
$breakpoint-lg: 768px;   // 大屏（iPad）
```

### 10.2 适配原则
1. **优先适配主流屏幕**：375px - 414px
2. **使用相对单位**：优先使用 rpx
3. **灵活布局**：使用 Flexbox 实现自适应
4. **测试验证**：在不同设备上测试

---

## 11. 主题定制

### 11.1 硬件类型主题

#### CPU 主题
```scss
.theme-cpu {
  --theme-primary: #667eea;
  --theme-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

#### GPU 主题
```scss
.theme-gpu {
  --theme-primary: #f093fb;
  --theme-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}
```

#### 手机主题
```scss
.theme-phone {
  --theme-primary: #4facfe;
  --theme-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}
```

---

## 12. 设计交付物

### 12.1 设计文件清单
- [ ] 页面原型图（Figma/Sketch）
- [ ] 视觉设计稿（完整 UI 设计）
- [ ] 切图资源（图标、背景图等）
- [ ] 设计规范文档（本文档）

### 12.2 开发协作
1. **设计稿标注**：使用 Figma/蓝湖进行标注
2. **切图输出**：提供 @2x、@3x 资源
3. **颜色变量**：提供 SCSS 变量表
4. **组件复用**：定义可复用组件

---

## 13. 设计检查清单

### 13.1 视觉检查
- [ ] 颜色使用符合设计系统
- [ ] 字体大小和字重统一
- [ ] 间距符合 8rpx 基准
- [ ] 圆角和阴影一致
- [ ] 品牌色正确应用

### 13.2 交互检查
- [ ] 所有可点击元素有点击反馈
- [ ] 页面切换动画流畅
- [ ] 加载状态有骨架屏或加载动画
- [ ] 错误提示友好
- [ ] 空状态有引导

### 13.3 响应式检查
- [ ] 在不同屏幕尺寸下测试
- [ ] 横屏模式适配
- [ ] 系统字体大小适配
- [ ] 深色模式兼容（可选）

---

## 14. 变更日志

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-02-06 | 初始版本创建 | 开发团队 |

---

## 15. 参考资料

- [微信小程序设计规范](https://developers.weixin.qq.com/miniprogram/design/)
- [Material Design](https://material.io/design)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [wot-design-uni 组件库](https://wot-design-uni.netlify.app/)

---

**文档结束**
