from django_assets import Bundle, register


class AssetBundles:
    # Use prebuilt/minified files from static/gen to avoid runtime resolver
    # recursion in webassets on this environment.
    base_scss = Bundle("gen/css/base.css")
    blog_js = Bundle("gen/scripts/blog.js")
    ty_js = Bundle("gen/scripts/typewriter.js")
    bundle_js = Bundle("gen/scripts/bundle.js")


register("base_scss", AssetBundles.base_scss)
register("blog_js", AssetBundles.blog_js)
register("ty_js", AssetBundles.ty_js)
register("bundle_js", AssetBundles.bundle_js)
