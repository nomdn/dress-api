import { minidenticon } from 'minidenticons';

/**
 * 根据用户名生成一个SVG头像的Data URL。
 * 
 * @param {string} username - 用于生成头像的用户名或唯一标识符。
 * @param {number|string} [saturation=95] - 颜色饱和度，范围0-100。
 * @param {number|string} [lightness=45] - 颜色亮度，范围0-100。
 * @returns {string} 返回一个 'data:image/svg+xml;utf8,...' 格式的Data URL字符串。
 */
function generateSvgAvatar(username, saturation = 95, lightness = 45) {
  // 1. 使用 minidenticon 函数生成原始的 SVG 字符串
  const svgString = minidenticon(username, saturation, lightness);
  
  // 2. 对 SVG 字符串进行 URI 编码
  // 注意：必须使用 encodeURIComponent，因为它会正确处理 SVG 中的特殊字符（如 '<', '>', '#', '{', '}' 等）
  const encodedSvg = encodeURIComponent(svgString);
  
  // 3. 拼接成完整的 Data URL
  return `data:image/svg+xml;utf8,${encodedSvg}`;
}

// 导出函数以便在其他地方使用
export { generateSvgAvatar };