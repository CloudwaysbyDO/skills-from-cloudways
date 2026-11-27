# Site audit checklist

Use this when `scripts/site_audit.py` cannot run, and to translate findings into business language for the email. Only report what you actually measured.

|| Check | How to tell | Why the business owner should care |
||---|---|---|
|| HTTPS | Site loads on https without redirect errors | Browsers show "Not secure" next to the address, which scares away customers |
|| SSL certificate expiry | Expires within 30 days or already expired | An expired certificate shows a full page security warning |
|| Server response time | Time to first byte over 1.5 seconds | Slow first response delays everything else |
|| Page weight | Home page HTML over 500 KB or many large images | Slow on mobile data, visitors leave before it loads |
|| PageSpeed mobile score | Under 50 is poor, 50 to 89 needs work | Google uses speed in ranking; slow sites lose visitors |
|| Mobile viewport | No `<meta name="viewport">` | Site is not built for phones, where most local searches happen |
|| Title tag | Missing, generic ("Home"), or over 65 characters | Weak or missing headline in Google results |
|| Meta description | Missing | Google picks random text for the search snippet |
|| H1 heading | None or several | Unclear page topic for search engines |
|| Image alt text | Many images without alt | Accessibility issue and lost image search traffic |
|| CMS version | Generator tag shows an old WordPress, Joomla or Drupal version | Outdated software is the most common way small business sites get hacked |
|| jQuery version | Below 3.0 | Sign of a site not updated in many years |
|| Copyright year | Footer year two or more years old | Visitors read it as "is this business still open?" |
|| Contact path | No form, no clickable phone (`tel:`) or email | Interested visitors have no easy way to get in touch |
|| Analytics | No Google Analytics, Tag Manager or similar | The owner cannot see where customers come from |
|| Booking or ecommerce | Industry normally takes bookings online but site does not | Competitors capture those customers |

## Turning findings into email lines

Write the business consequence, not the technical term.

- Weak: "Your site has no meta viewport tag."
- Strong: "On my phone your homepage loads at desktop size, so the menu and phone number are tiny."

- Weak: "Your WordPress version is 5.2."
- Strong: "Your site runs a version of WordPress from 2019, which no longer gets security fixes."

Pick the one or two findings with the clearest business impact. Three or more reads like a lecture.