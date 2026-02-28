## Version 4

### v4.1
- **Breaking:** Added a `blog_enabled` site setting in admin to fully disable blog navigation and blog routes when turned off.
- **Major:** Refined admin settings behavior to prioritize database-managed values over static config fallbacks.
- **Major:** Reworked API documentation experience with deeper theming integration, layout cleanup, and readability improvements.
- **Major:** Expanded and organized public API coverage and docs structure (Roblox, Twitch, Steam, BTTV, FFZ, 7TV).
- **Major:** Improved OAuth/provider setup flow to support app-linking patterns with admin-first credential handling.
- **Major:** Rebuilt now-playing/game status UI behavior for cleaner stacking, positioning, and state visibility when inactive.
- **Major:** Added/improved profile aura auto-color extraction and propagated theme accent usage across key UI elements.
- **Major:** Improved navbar/link rendering consistency and removed browser-default link styling regressions.
- **Major:** Updated path handling to avoid hardcoded absolute deployment paths where possible.
- **Major:** Redesigned Specs pages with modern card/table/gallery layouts and better empty states.
- **Major:** Redesigned Bots/Twitch bot pages with cleaner cards, status badges, and clearer action links.
- **Minor:** Improved cleanup/maintenance workflow for generated and unused assets.
- **Minor:** Synced markdown/legal/changelog publishing flow for website documents.

### v4.0
- **Breaking:** Migrated core app credential management to admin-first configuration, with `config.ini` as fallback.
- **Major:** Added OAuth/provider config fields to admin-managed API credentials and expanded provider support.
- **Major:** Reworked API docs rendering/theming and improved OpenAPI schema generation for route parameters.
- **Major:** Added/expanded public API endpoints (BTTV, FFZ, 7TV, Steam integrations).
- **Major:** Added automatic profile-picture aura color extraction from the active avatar.
- **Minor:** Improved project hygiene with expanded ignore rules and cleanup tooling for generated/static artifacts.

---

## Version 3

### v3.3
- **Breaking:** Introduced a loading container with a fade-out animation for smooth page transitions. This new feature enhances user experience by providing a seamless transition between pages.
- **Major:** Enhanced error page handling with detailed messages and contextual information. The error pages now offer more information about the encountered issues, helping users understand and resolve problems.
- **Major:** Implemented middleware to gracefully handle unauthorized access. This improvement ensures a user-friendly experience when encountering access restrictions, such as a 401 error, especially in the admin section.
- **Major:** Added support for showing/hiding the password input with eye icons in the login page. This feature improves user convenience and security during the login process.
- **Minor:** Styled auto-fill blanks with a custom color, changing the default yellow to a distinctive #fe5186, aligning with the overall aesthetic of the website.
- **Minor:** Adjusted margins for specific design elements, fine-tuning the spacing to improve the overall visual balance of the pages.
- **Minor:** Applied rounded corners to specific SVG icons, enhancing the visual appeal of these elements.

### v3.2.2
- **Minor:** Added a copyright/legal page, providing users with essential legal information and improving transparency.

### v3.2.1
- **Major:** Added the changelog to keep track of updates and changes made to the website.
- **Bugfix:** Fixed a 500 error on `/changelog`, ensuring users can access the changelog page without encountering issues.

### v3.2
- **Major:** Added borders and background to all aspects of the website, creating a cohesive and visually appealing design.
- **Major:** Added the changelog to keep track of updates and changes made to the website.
- **Minor:** Added a version icon for a touch of branding and visual recognition.
- **Minor:** Added a copyright/legal page, providing users with essential legal information and improving transparency.
- **Minor:** Added versioning for better tracking and management of updates.
- **Bugfix:** Fixed a 500 error on `/changelog`, ensuring users can access the changelog page without encountering issues.


### v3.0
- **Breaking:** Added an API page and endpoints, expanding the website's functionality and allowing interaction with external applications.
- **Major:** Added API Docs, providing users with comprehensive documentation on available APIs.


---

## Version 2
### v2.3
- **Major:** Added a Projectes page to show the current projects i have wored on or am working on
- **Major:** Added a Specs page for computer speace 
- **Major:** Added a Bots page for for bots i host 


### v2.2
- **Major:** Changed most of the website to use Django variables `{{ var_name }}`, improving code consistency and maintainability.

### v2.1
- **Major:** Added an about page, providing users with additional information about the owner.

### v2.0
- **Breaking:** Moved the website hosting from Cloudflare to Django, ensuring better control and management.
- **Breaking:** Introduced a new theme for a refreshed visual experience.

---

## Version 1

### v1.2
- **Major:** Switched the contact page to the home page, improving navigation and user engagement.

### v1.1.1
- **Minor:** Added a glitch effect to the name for a unique visual touch.
- **Minor:** Added a hover effect to the navbar, enhancing interactivity.

### v1.1
- **Major:** Added a contact page, allowing users to get in touch easily.

### v1.0
- **Breaking:** Created the site, marking the initial launch and introduction of the website to users.

