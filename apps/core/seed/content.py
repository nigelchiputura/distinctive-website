"""The old site's real content, loaded by `manage.py seed_site_content`
(docs/Phase_1/Task_Breakdown.md, Days 5, 6 and 9).

Text is the old site's (distinctive.co.zw, captured 2026-10-06), with spelling and spacing tidied.
Images in seed/images/ were cut from screenshots of the old site, so they are small: the client
replaces them with the original files in the admin (Phase 1 Q5). The Home hero photo is left out
because the old site printed its text over it; the slide shows on a plain background until the
original photo is uploaded.

Each item has a key the seed uses to tell whether it's already there (a section's anchor, a slide's
heading, a service's anchor, a person's name, a logo's kind and name). Day 5 seeded Home, Day 6
About; Days 7 and 9 add Services and Contact.
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


# ---- About (Day 6) -------------------------------------------------------------------------
# The hero photo is left out for the same reason as Home's: the old site printed its heading
# over it.

ABOUT_META_DESCRIPTION = (
    "Distinctive Consultancy Services is a Zimbabwean human resources consultancy, founded in "
    "2006, with a presence in Zambia and Mozambique. Meet our leadership."
)

ABOUT_SECTIONS: tuple[dict[str, Any], ...] = (
    {
        "anchor": "welcome",
        "section_type": "hero_text",
        "heading": "Bringing Excellence Into Your World!",
        "sort_order": 10,
    },
    {
        "anchor": "our-story",
        "section_type": "two_column",
        "heading": "Our Story",
        "intro": "Distinctive Consultancy Services is a Zimbabwean Business Consultancy Firm "
        "that specialises in Human Resources Consultancy Services. Established in July 2006, it "
        "commenced operations in May 2008. Our core business is offering a wide range of "
        "strategic management and specialised and unique Human Resources solutions, customised "
        "to meet differing and varying customer needs.",
        "body": "Distinctive Consultancy Services is not only under the leadership of innovative "
        "female directors, but is also gender sensitive in all its business conduct. The firm "
        "has experienced continuous, sustained growth, which has seen the establishment of a wide "
        "network of multifaceted organisations across various sectors of the economy, covering "
        "**Non-governmental Organisations**, **Parastatals**, and the **Private and Public "
        "Sectors**. The evident growth of Distinctive is a result of distinguished service "
        "delivery, characterised by the provision of robust and unique solutions that are tailor "
        "made to meet the specific needs of our clients. With the advent of COVID-19 we have "
        "embraced relevant **online service delivery** techniques as well as the provision of "
        "solutions electronically.\n\n"
        "Our aggressive **regional expansion** is evidenced by our presence in **Zambia** under "
        "the banner Distinctive Zambia, and in **Mozambique** through a strategic partnership. "
        "Our aim is to be available to serve our Zimbabwean clients when they open up in new "
        "territories, in Africa and beyond. We also boast an international flair, having "
        "brokered international partnerships.",
        "sort_order": 20,
    },
    {
        "anchor": "strategic-partners",
        "section_type": "partners",
        "heading": "Strategic Partners",
        "heading_align": "center",
        "sort_order": 30,
    },
    {
        "anchor": "capability-analysis",
        "section_type": "band_dark",
        "heading": "Capability Analysis",
        "body": "Distinctive Consultancy Services has the capability to:\n\n"
        "- Leverage the collective competencies of a highly qualified and experienced team of "
        "consultants from multi-sector backgrounds, with diverse skills and competencies in "
        "People and Culture Management and an average practice period of over 20 years.\n"
        "- Provide tailor-made, practice-based People Management Solutions, customised to "
        "specific client needs and requirements.\n"
        "- Transfer knowledge and build capacity in client organisations.\n"
        "- Innovate with the client in problem identification and solution finding.\n\n"
        "The wealth of experience is balanced by a team of young, vibrant consultants of the "
        "digital age, with an electronic flair, a plethora of talent and modern ideas. The "
        "gender mix, with both sexes represented, produces a balanced culture.",
        "image": "capability-analysis.jpg",
        "image_alt": "Colleagues in silhouette working together against a city skyline",
        "image_position": "left",
        "sort_order": 40,
    },
    {
        "anchor": "value-driven",
        "section_type": "band_dark",
        "heading": "Value Driven and Capacity Building",
        "heading_align": "right",
        "body": "Distinctive Consultancy creates and delivers value to its clients by offering "
        "practical, solution-based, value-added and cost-effective services (advisory and direct "
        "involvement). The service package is buttressed by free after-service backup and "
        "support. Our service delivery is not just focused on solving immediate problems for the "
        "client, but is structured to capacitate the client organisation through knowledge "
        "transfer from consultant to client. The value is captured in diminishing dependence on "
        "the consultant.",
        "sort_order": 50,
    },
    {
        "anchor": "our-leadership",
        "section_type": "team",
        "heading": "Our Leadership",
        "heading_align": "center",
        "sort_order": 60,
    },
)

PARTNERS: tuple[dict[str, Any], ...] = (
    {
        "kind": "partner",
        "name": "Emergence Growth",
        "caption": "Emergence Growth",
        "image": "emergence-growth.png",
        "image_alt": "Emergence Growth logo",
        "sort_order": 10,
    },
    {
        "kind": "partner",
        "name": "Bindura University of Science Education",
        "caption": "Bindura University of Science Education",
        "image": "bindura-university.png",
        "image_alt": "Bindura University of Science Education crest",
        "sort_order": 20,
    },
)

# The old site's bios, with spacing and punctuation tidied. The old page spells the board
# member "Norbet" in his heading and "Nobert" in his bio: kept as found until the client
# confirms (Phase 1 Q9). The old page had Facebook and LinkedIn icons for two people but their
# links aren't in the screenshots; the client adds them in the admin.
TEAM: tuple[dict[str, Any], ...] = (
    {
        "name": "Rose Nhamo",
        "title": "Group Managing Consultant (Executive Director)",
        "image": "rose-nhamo.jpg",
        "image_alt": "Rose Nhamo",
        "bio": "Rose has worked in various capacities in both the public and private sectors. "
        "She has held senior positions both in formal employment and in consultancy assignments "
        "in the public sector and leading private sector organisations, as well as NGOs. Rose "
        "has sat on the boards of various organisations in the insurance, mining, state-owned "
        "enterprise, banking and transport industries (Pioneer Corporation Africa, CBZ "
        "Holdings, Legal Resources Foundation, Tropical Reinsurance). She has conducted "
        "organisational development and assessment assignments for various organisations. She "
        "is the Group Managing Consultant of Distinctive Consultancy Services. She is a Fellow, "
        "and served as President of the Institute of People Management Zimbabwe (IPMZ) from "
        "2011 to 2013. Rose is a Commissioner on the Competition and Tariff Commission, sits on "
        "the Board of the Procurement Regulatory Authority of Zimbabwe, and was appointed to "
        "the Board of NAMACO (National Manpower Advisory Council) from August 2012 to December "
        "2015.\n\n"
        "Rose was also part of the National Labour Law Advisory Council in 2016, which had a "
        "mandate to come up with amendments to the Labour Act. She was on the Human Resources "
        "Committee of the Medicines Control Authority of Zimbabwe (MCAZ) from March 2015 to "
        "March 2016. She received the African Leadership Award for Education in 2014 and the "
        "Human Resources Leader and Achiever Award in 2011.",
        "sort_order": 10,
    },
    {
        "name": "Farai Pilime",
        "title": "Operations Director (Executive Director)",
        "image": "farai-pilime.jpg",
        "image_alt": "Farai Pilime",
        "bio": "Farai holds an MBA from the University of Gloucestershire. She has over 20 years' "
        "customer service, sales and marketing experience at executive level. She has held "
        "senior executive roles in the transport and banking industries (National Tyre "
        "Services, Pioneer Freight and Unifreight), and has also worked for Standard Chartered "
        "Bank. Farai is a research expert with a proven track record in business development. "
        "As head of the sales and marketing functions she was responsible for public relations "
        "and organised events and functions for the organisations she worked for. She was also "
        "responsible for communication and the management of key stakeholder relationships "
        "(customers, media partners, suppliers and communities). Farai successfully implemented "
        "and managed customer service systems in organisations. She has experience in the "
        "management of multi-site operations, marketing and sales, and production and "
        "operations, in senior executive positions.",
        "sort_order": 20,
    },
    {
        "name": "Dr. Givemore Taputaira",
        "title": "Board Chairman",
        "image": "givemore-taputaira.jpg",
        "image_alt": "Dr. Givemore Taputaira",
        "bio": "Givemore is the Board Chairman of Edu-dynamics Business School and of "
        "Distinctive Consultancy Services. He has vast experience in project management, "
        "digital solutions and leading multimillion-dollar projects across Africa. He has "
        "worked as Technical Director, and then Development Director, for a leading hospitality "
        "group, and is now the Managing Director of Digital Edge Solutions. He has successfully "
        "led business strategy, change and design thinking projects both locally and in Africa. "
        "He holds a Bachelor of Science degree and an MBA from the University of Zimbabwe. "
        "Givemore sits on the boards of listed organisations in the banking and hospitality "
        "industries, and has worked in various senior executive capacities in the private "
        "sector.",
        "sort_order": 30,
    },
    {
        "name": "Norbet Muyaka",
        "title": "Board Member",
        "image": "norbet-muyaka.jpg",
        "image_alt": "Norbet Muyaka",
        "bio": "Nobert has worked in key African markets (South Africa, Zambia, Botswana, "
        "Namibia, Malawi). He has experience in positioning and transforming businesses into "
        "world-class brands, and over 15 years of senior management experience in FMCG, private "
        "and public sector organisations. He holds a Master's in Business Leadership from "
        "UNISA. He has a proven track record in strategic marketing planning, brand development "
        "and management, customer relationship management, marketing research, international "
        "marketing, agency management and marketing communications planning.",
        "sort_order": 40,
    },
    {
        "name": "Rebecca Matongo",
        "title": "Board Member",
        "image": "rebecca-matongo.jpg",
        "image_alt": "Rebecca Matongo",
        "bio": "Rebecca, a marketer by profession, is a seasoned business professional with an "
        "established track record at executive management level in the pharmaceutical, "
        "beverages and food industries. She is the Head of Marketing, Sales and Distribution "
        "for Star Africa. She holds an MBA from Nottingham Trent University, UK, and a "
        "marketing degree from the University of South Africa. Rebecca also sits on the "
        "Confederation of Zimbabwe Industries (CZI) Membership and Marketing Committee. She "
        "currently serves as the Area Secretary for the Southern and East Africa Area of the "
        "World Federation of Methodist and Uniting Church Women, and is Vice Area President "
        "elect (2021–2026).",
        "sort_order": 50,
    },
    {
        "name": "Tawanda Pilime",
        "title": "Board Member",
        "image": "tawanda-pilime.jpg",
        "image_alt": "Tawanda Pilime",
        "bio": "Tawanda is an IT specialist with 20 years' experience. He holds an International "
        "Diploma in Computer Science and has developed IT systems for private sector "
        "organisations. Among other successful projects, he has taken an active part in "
        "customising AMS (Asset Management System) for banking institutions, and has "
        "programmed and implemented the SmartFTMS application system for a listed corporation. "
        "He has successfully run software development projects and network systems in Zimbabwe "
        "and Zambia.",
        "sort_order": 60,
    },
    {
        "name": "Nomatter Sigauke",
        "title": "Board Member",
        "image": "nomatter-sigauke.jpg",
        "image_alt": "Nomatter Sigauke",
        "bio": "Nomatter is a Chartered Accountant with experience in strategic management, "
        "financial management, corporate finance, investments and organisational "
        "transformation. He holds a BCom Accounting Honours degree. Nomatter is Head of Finance "
        "for Zimnat Asset Management and an Optimisation Champion at Masawara Holdings. He has "
        "also worked for Deloitte & Touche. He is a member of ICAZ's Audit and Professional "
        "Standards Committee (APSC).",
        "sort_order": 70,
    },
    {
        "name": "Florence Jambwa",
        "title": "Board Member",
        "image": "florence-jambwa.jpg",
        "image_alt": "Florence Jambwa",
        "bio": "Florence is an astute and well-experienced company secretary and legal adviser "
        "with demonstrated knowledge of working in the quasi-government and government "
        "administration sector. She is skilled in legal writing, legal services, business law, "
        "tax law, municipal law, corporate governance and alternative dispute resolution (ADR). "
        "A strong business development professional, she holds a Master of Laws in "
        "International Business Law from the University of Cumbria, UK.",
        "sort_order": 80,
    },
)
