"""The old site's real content, loaded by `manage.py seed_site_content`
(docs/Phase_1/Task_Breakdown.md, Days 5, 6 and 9).

Text is the old site's (distinctive.co.zw, captured 2026-10-06), with spelling and spacing tidied.
Images in seed/images/ were cut from screenshots of the old site, so they are small: the client
replaces them with the original files in the admin (Phase 1 Q5). The Home hero photo is left out
because the old site printed its text over it; the slide shows on a plain background until the
original photo is uploaded.

Each item has a key the seed uses to tell whether it's already there (a section's anchor, a slide's
heading, a service's anchor). Day 6 adds About, Day 9 Services and Contact.
"""

from typing import Any

HOME_META_DESCRIPTION = (
    "Distinctive Consultancy Services, Harare: industrial and employee relations, HR audits, "
    "talent acquisition, people strategy, research surveys and organisational design."
)

HOME_SLIDES: tuple[dict[str, Any], ...] = (
    {
        "heading": "Distinctive Consultancy Services",
        "subheading": "Bringing excellence into your world.",
        "sort_order": 10,
    },
)

HOME_SECTIONS: tuple[dict[str, Any], ...] = (
    {
        "anchor": "services",
        "section_type": "service_cards",
        "sort_order": 10,
    },
    {
        "anchor": "get-in-touch",
        "section_type": "cta",
        "heading": "Get the best specialised business consultancy services in Africa.",
        "button_label": "Get In Touch",
        "button_url": "/contact/",
        "sort_order": 20,
    },
    {
        "anchor": "people-centred",
        "section_type": "value_block",
        "heading": "People Centred",
        "body": "We recognise and cherish the human dimension of our business and thrive on its "
        "quest for never-ending growth and prosperity.",
        "image": "people-centred.jpg",
        "image_alt": "Silhouettes of people helping one another up a rocky hill at sunset",
        "image_position": "left",
        "sort_order": 30,
    },
    {
        "anchor": "proactive",
        "section_type": "value_block",
        "heading": "Proactive",
        "body": "We move ahead of events and strive to change faster than the rate of change in "
        "our domain of practice.",
        "image": "proactive.jpg",
        "image_alt": "Colleagues discussing charts and reports around a table",
        "image_position": "right",
        "sort_order": 40,
    },
)

# The six services on Home's cards. Day 7 adds the rest of the 13 and every service's full text.
SERVICES: tuple[dict[str, Any], ...] = (
    {
        "anchor": "industrial-employee-relations",
        "title": "Industrial / Employee Relations",
        "summary": "We assess the state of IR in an organisation and give relevant advice.",
        "image": "employee-relations.jpg",
        "image_alt": "Hands together holding a seedling, with the words Employee Relations",
        "show_on_home": True,
        "sort_order": 10,
    },
    {
        "anchor": "hr-audits",
        "title": "HR Audits",
        "summary": "HR compliance auditing solutions that meet the needs of your organisation.",
        "image": "hr-audits.jpg",
        "image_alt": "A hand touching the letters HR among human resources icons",
        "show_on_home": True,
        "sort_order": 20,
    },
    {
        "anchor": "talent-acquisition",
        "title": "Talent Acquisition",
        "summary": "Culture and candidate profile analysis for placements and assessments.",
        "image": "talent-acquisition.jpg",
        "image_alt": "A chalkboard with the words Talent Management",
        "show_on_home": True,
        "sort_order": 30,
    },
    {
        "anchor": "people-strategy",
        "title": "People Strategy",
        "summary": "Enable employees to excel and focus on organisational goals.",
        "image": "people-strategy.jpg",
        "image_alt": "A hand arranging wooden blocks marked with people",
        "show_on_home": True,
        "sort_order": 40,
    },
    {
        "anchor": "research-surveys",
        "title": "Research Surveys",
        "summary": (
            "Employee engagement, culture audits, salary surveys, mystery shopping and more."
        ),
        "image": "research-surveys.jpg",
        "image_alt": "Open hands beneath a network of people icons",
        "show_on_home": True,
        "sort_order": 50,
    },
    {
        "anchor": "organisational-design",
        "title": "Organisational Design",
        "summary": (
            "Structurally designed to advise on all areas of business design and rightsizing."
        ),
        "image": "organisational-design.jpg",
        "image_alt": "Three business people in silhouette by an office window",
        "show_on_home": True,
        "sort_order": 60,
    },
)
