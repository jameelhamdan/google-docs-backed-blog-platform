# google-docs-backed-blog-platform

<h2>Our idea:</h2>
<p>We want to make a blog platform similar to medium.com but uses Google Docs API for writing articles (optional main feature)</p>

<h2>Similar projects:</h2>
<p>https://github.com/gkiely/ydnw (we basically need to make an app similar to this app but better)</p>

<h2>Helpful packages:</h2>
<ul>
    <li>https://github.com/nesdis/djongo</li>
    <li>https://github.com/oauthlib/oauthlib</li>
</ul>

<h2>Features (hopefully):</h2>
<ol>
<li>Register as a user and hook Gmail account.</li>
<li>View other people blogs and articles and see the most popular blogs.</li>
<li>Adding Articles to user blog and using a google document.</li>
<li>Programmatically add Trigger on user google document save to send a request us to check for changes and update the document.</li>
<li>User “admin” panel where they can manage added articles and check reactions and traffic on their blog, and be able to delete/publish/add new articles to their blogs.</li>
</ul>

<h2>Suggested Technologies:</h2>
<ul>
<li>Django as the main web framework (has good SEO built-in)</li>

<li>Use PostgreSQL for the user and Gmail auth, and use MongoDB for article and blog data storage</li>

<li>Use https://editorjs.io/ as an alternative to Google Doc editing</li>
</ul>
