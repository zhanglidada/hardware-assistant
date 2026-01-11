/// <reference types="vite/client" />

declare module '*.vue' {
  import { DefineComponent } from 'vue'
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/ban-types
  const component: DefineComponent<{}, {}, any>
  export default component
}

// wot-design-uni 组件库类型声明
declare module 'wot-design-uni' {
  import { Plugin } from 'vue'
  const WotDesignUni: Plugin
  export default WotDesignUni
}

// wot-design-uni 组件类型
declare module 'wot-design-uni/components/*' {
  import { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// uni-app 全局 API 类型声明
declare const uni: typeof import('@dcloudio/uni-app')['uni']
