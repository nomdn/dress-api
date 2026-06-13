import type { SitemapUrlInput } from '#sitemap/types'
// server/api/__sitemap__/urls.ts
import { defineSitemapEventHandler } from '#imports'

export default defineSitemapEventHandler(async () => {
    const config = useRuntimeConfig()
    let data: Record<string, string>
    try{
        data = await $fetch(config.remote.remoteURL+'index_1.json')
    }catch(e){
        console.error('Failed to fetch data for sitemap:', e)
        try{
            data = await $fetch(config.rollback.remoteURL+'index_1.json')
        }
        catch(e){
            console.error('Failed to fetch rollback data for sitemap:', e)
            data = {} // Fallback to an empty map if both fetches fail
        }
    }
    const authors = Object.keys(data)
    const sitemapUrls: SitemapUrlInput[] = []
    for (const author of authors) {
        const url = `/author/${author}`
        sitemapUrls.push({
            loc: url,
            _sitemap: 'authors'
        })
    }
    return sitemapUrls
})
