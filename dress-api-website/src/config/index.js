/**
 * Dress API 客户端配置
 * 
 * 该配置用于控制前端如何与 Dress 图片服务交互。
 * - `useMinimum`: 启用“最简模式”（Minimal Mode），此时完全依赖远程 API，不使用本地资源。
 * - `remote`: 主服务地址（推荐使用，响应更快、功能完整）。
 * - `rollback`: 回退地址（当主服务不可用时可手动切换，通常指向 jsDelivr CDN）。
 */
const config = {
    // 是否启用最简模式（Minimal Mode）：
    // - true: 所有数据和图片均从 remote 或 rollback 指定的远程 URL 获取
    // - false: 可能尝试使用本地托管的资源（需配合后端非 lite_mode）
    useLite: false,

    // 主服务配置（生产环境推荐地址）
    remote: {
        remoteURL: 'https://api.wsmdn.top/',     // API 根地址
        imgURL: 'https://fastly.jsdelivr.net/gh/Cute-Dress/Dress@master/'     // 本地托管图片的访问前缀（仅在非 lite 模式下有效）
    },

    // 回退服务配置（CDN 备用地址，适用于主服务宕机或网络受限场景）
    rollback: {
        remoteURL: 'https://testingcf.jsdelivr.net/gh/nomdn/dress-api@main/', // 这里的RemoteAPI只用于获取json数据，使用v1标准，即直接获取url/index_*.json
        imgURL: 'https://fastly.jsdelivr.net/gh/Cute-Dress/Dress@master/'
    }
};

export default config;