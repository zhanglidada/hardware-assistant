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

// 微信小程序全局对象类型声明
declare const wx: {
  cloud?: {
    init: (config: {
      traceUser?: boolean;
      env?: string;
    }) => void;
    database: () => {
      collection: (name: string) => {
        get: (options?: {
          success?: (res: any) => void;
          fail?: (err: any) => void;
          complete?: () => void;
        }) => Promise<{
          data: any[];
          errMsg: string;
        }>;
        add: (options: {
          data: any;
          success?: (res: any) => void;
          fail?: (err: any) => void;
          complete?: () => void;
        }) => Promise<{
          _id: string;
          errMsg: string;
        }>;
        doc: (id: string) => {
          get: (options?: {
            success?: (res: any) => void;
            fail?: (err: any) => void;
            complete?: () => void;
          }) => Promise<{
            data: any;
            errMsg: string;
          }>;
          remove: (options?: {
            success?: (res: any) => void;
            fail?: (err: any) => void;
            complete?: () => void;
          }) => Promise<{
            stats: {
              removed: number;
            };
            errMsg: string;
          }>;
        };
        where: (condition: any) => any;
        skip: (num: number) => any;
        limit: (num: number) => any;
        orderBy: (field: string, order: 'asc' | 'desc') => any;
        count: () => Promise<{
          total: number;
          errMsg: string;
        }>;
      };
    };
  };
}
