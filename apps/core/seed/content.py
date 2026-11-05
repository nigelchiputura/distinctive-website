"""The old site's real content, loaded by `manage.py seed_site_content`
(docs/Phase_1/Task_Breakdown.md, Days 5, 6 and 9).

Text is the old site's (distinctive.co.zw, captured 2026-10-06), with spelling and spacing tidied.
Images in seed/images/ were cut from screenshots of the old site, so they are small: the client
replaces them with the original files in the admin (Phase 1 Q5). The Home hero photo is left out
because the old site printed its text over it; the slide shows on a plain background until the
original photo is uploaded.

Each item has a key the seed uses to tell whether it's already there (a section's anchor, a slide's
heading, a service's anchor, a person's name, a logo's kind and name). An item that is already
there gets only its **empty** text fields and a missing image filled in (Day 7 added the full text
to services Day 5 had created); nothing an editor has filled in is changed. Day 5 seeded Home,
Day 6 About, Day 7 Services; Day 9 adds Contact.
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

# The 13 services from the old Services page (Day 7). The first six (Day 5) are Home's cards;
# Day 7 added the full text to them and the other seven. The text is the old page's, tidied;
# NGO Capacity Development's text is written out from its diagram, so the content isn't only in
# an image. The order groups related services; the old page's order differed, and editors set
# their own in the admin.
SERVICES: tuple[dict[str, Any], ...] = (
    {
        "anchor": "industrial-employee-relations",
        "title": "Industrial / Employee Relations",
        "summary": "We assess the state of IR in an organisation and give relevant advice.",
        "body": "We assess the state of industrial relations in an organisation and give advice "
        "on disciplinary matters, works councils, grievances, codes of conduct and related "
        "issues. We also offer:\n\n"
        "- Designing codes of conduct\n"
        "- Training for works councils (including legal connotations, the works council "
        "constitution, conflict management, payroll management, negotiations and communication)\n"
        "- Disciplinary management training (including preferring the right charges, the rules "
        "of natural justice, understanding labour laws and understanding the code of conduct)",
        "image": "employee-relations.jpg",
        "image_alt": "Hands together holding a seedling, with the words Employee Relations",
        "show_on_home": True,
        "sort_order": 10,
    },
    {
        "anchor": "services-for-the-nec",
        "title": "Services for the NEC",
        "body": "We offer breadth and depth of knowledge and experience in the issues that help "
        "the administration and secretarial side of NECs. Our specialist services are:\n\n"
        "- NEC administration\n"
        "- CBA drafting\n"
        "- Personal injury and workman's compensation\n"
        "- Drafting and reviewing codes of conduct\n"
        "- Policy drafting\n"
        "- Conciliation, mediation and arbitration\n"
        "- Working hours related to COVID-19\n"
        "- Job evaluation for NECs\n"
        "- Labour Act pre-empting\n"
        "- Health and safety practices linked to COVID-19 and other pandemics\n"
        "- COVID-19 related misconduct\n"
        "- COVID-19 and reasonable accommodation",
        "sort_order": 12,
    },
    {
        "anchor": "learning-and-development",
        "title": "Learning and Development (Training)",
        "body": "We aim to improve group and individual performance by honing skills and "
        "knowledge. We provide employees at all levels with tools and skills, showing them how "
        "to apply those tools within their department, organisation and role. E-learning "
        "platforms are available to make the transfer of knowledge and skills easier. "
        "Distinctive Consultancy provides customised solutions for the specific needs of each "
        "and every organisation.\n\n"
        "**Training products on offer:**\n\n"
        "- Evidence Based Training\n"
        "- Training Needs Analysis\n"
        "- Personal Development\n"
        "- Grooming and Deportment\n"
        "- Powerful Personal Presentations\n"
        "- Effective Report Writing Skills\n"
        "- Corporate Governance Skills\n"
        "- Change Management\n"
        "- Disciplinary Management\n"
        "- Workers Committee\n"
        "- Public Relations\n"
        "- Presentation Skills\n"
        "- Customer Care\n"
        "- Management Development\n"
        "- Personal Development and Effectiveness\n"
        "- Problem Solving and Decision Making\n"
        "- Effective Planning and Budgeting\n"
        "- HR for Non-HR People\n"
        "- Strategic Planning Skills",
        "sort_order": 14,
    },
    {
        "anchor": "organisational-development",
        "title": "Organisational Development",
        "body": "We have the capability to undertake most organisational development activities, "
        "such as:\n\n"
        "- **Performance management**\n"
        "- **Change management**\n"
        "- **Policy and procedure development**: remote work, occupational health and safety, "
        "leave, employee onboarding and many more\n"
        "- **Balanced scorecard development**",
        "sort_order": 16,
    },
    {
        "anchor": "hr-audits",
        "title": "HR Audits",
        "summary": "HR compliance auditing solutions that meet the needs of your organisation.",
        "body": "**Distinctive Consultancy Services** provides HR compliance auditing solutions "
        "that meet the needs of your organisation, and reviews employers' human resources "
        "functions to ensure compliance with the latest labour and employment laws and "
        "alignment with organisational goals. We provide full-service HR compliance audits to "
        "assess the employment practices, compliance and human resources functions within an "
        "organisation.\n\n"
        "HR audits can focus on staffing, regulatory compliance, cost savings, organisational "
        "objectives or other human resources issues. Human resources audits should be performed "
        "regularly to avoid costly legal disputes. They are particularly valuable after "
        "significant changes in an organisation, such as a restructuring, an expansion or a "
        "reduction in force.",
        "image": "hr-audits.jpg",
        "image_alt": "A hand touching the letters HR among human resources icons",
        "show_on_home": True,
        "sort_order": 20,
    },
    {
        "anchor": "organisational-design-and-restructuring",
        "title": "Organisational Design and Restructuring",
        "body": "This is an area of specialty for us.\n\n"
        "At some point, all organisations either mature or need to rethink their business model "
        "or processes, grow, shrink or change, and as we all know, one size does not fit all!\n\n"
        "Restructuring and making redundancies can be a difficult process for both employers and "
        "employees, even those who are not directly affected. It can affect morale and "
        "productivity, and take considerable management time, affecting the day-to-day running "
        "of the business. We can help by leading the entire restructuring or redundancy process, "
        "or by providing guidance or resources at a particular stage.",
        "sort_order": 22,
    },
    {
        "anchor": "team-building",
        "title": "Team Building",
        "body": "Successful results in business are usually accomplished through teamwork. We "
        "provide themed, energising and results-oriented team building sessions for small and "
        "large teams.",
        "sort_order": 24,
    },
    {
        "anchor": "outsourced-hr-services",
        "title": "Outsourced HR Services",
        "body": "Do you lack the time and experience to deal with some or all of your human "
        "resources activities? Then outsourcing your HR can be the right move for your company. "
        "**Distinctive Consultancy Services** can take care of all your HR requirements, "
        "allowing you to concentrate on growing your company's profitability and productivity. "
        "We provide a comprehensive range of outsourcing services, from payroll and benefits "
        "administration to designing and arranging contracts, hiring, recruitment and training. "
        "We provide ongoing support packages for organisations in Africa with or without an "
        "existing HR department or HR function, so your organisation benefits from packages "
        "tailored to its size, structure, business needs and budget.",
        "sort_order": 26,
    },
    {
        "anchor": "talent-acquisition",
        "title": "Talent Acquisition",
        "summary": "Culture and candidate profile analysis for placements and assessments.",
        "body": "Distinctive Consultancy Services also does placements and assessments. Our "
        "emphasis is on investing our time and effort in getting to know our customers and their "
        "needs very well. We give support for the successful execution of a product or "
        "programme. We also take the time to study our clients' culture and analyse candidates' "
        "profiles to make sure they will fit into the organisation. To achieve this we headhunt "
        "candidates, use our existing database and advertise to find new candidates who fit the "
        "role. We have candidates with vast regional experience. We can also assist with "
        "replacing employees if there are any shortfalls in personnel.\n\n"
        "We provide private facilities for interviews and can also take part in them. We conduct "
        "thorough background checks to make sure the correct candidate is hired. We offer "
        "psychometric tests for our clients, provided by our strategic partner EPZ Global.",
        "image": "talent-acquisition.jpg",
        "image_alt": "A chalkboard with the words Talent Management",
        "show_on_home": True,
        "sort_order": 30,
    },
    {
        "anchor": "people-strategy",
        "title": "People Strategy",
        "summary": "Enable employees to excel and focus on organisational goals.",
        "body": "We perform and go beyond strategic reviews and strategic planning sessions for a "
        "wide variety of progressive organisations. We believe that people are the most "
        "important part of the formula for business success. Organisations should be equipped "
        "to select the right people, enable those people to excel and get them to focus on the "
        "right goals. In that regard we help organisations with:\n\n"
        "- Strategic planning facilitation\n"
        "- Team building\n"
        "- Culture audits\n"
        "- Executive coaching\n"
        "- Organisational effectiveness\n"
        "- Organisation structure design\n"
        "- Human capital strategy\n"
        "- Goal alignment\n"
        "- Employee retention strategies\n"
        "- Change management",
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
        "body": "Distinctive Consultancy provides business research surveys.\n\n"
        "- Methodologies include face-to-face and telephone interviews, mail questionnaires and "
        "online forms, paying due regard to prevailing economic changes, and tailored to the "
        "client's needs.\n"
        "- Employee engagement, culture audit, salary, mystery shopping, market analysis, "
        "baseline, brand loyalty and client satisfaction surveys are regularly undertaken.\n"
        "- Reports are succinct, with a full analysis of the data gathered in graphs and tables, "
        "and conclusions and recommendations.\n"
        "- All fieldwork is conducted by a team of interviewers experienced in surveys in the "
        "world of business.\n"
        "- *Our questionnaires purposely go from open and projective questions to more "
        "close-ended and focused ones.*\n"
        "- *The questionnaire is open enough to let respondents express their views without "
        "being overly influenced.*",
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
        "body": "We have structurally designed our firm "
        "to advise clients on all areas of organisational design and rightsizing. We provide "
        "specialist services to employers and employees on these issues:\n\n"
        "- Retrenchment and redundancy\n"
        "- How to retrench during the COVID-19 pandemic\n"
        "- Training on alternatives to job losses\n"
        "- Retrenchment package calculation\n"
        "- Organisational change management\n"
        "- How to manage legal and reputational risks when downsizing",
        "image": "organisational-design.jpg",
        "image_alt": "Three business people in silhouette by an office window",
        "show_on_home": True,
        "sort_order": 60,
    },
    {
        "anchor": "ngo-capacity-development",
        "title": "NGO Capacity Development Partners",
        "body": "We work with non-governmental organisations to develop their capacity in five "
        "areas:\n\n"
        "- **Corporate governance:** board training; board induction and evaluation\n"
        "- **Capacity building:** the basic principles of running small businesses; finance for "
        "non-finance staff\n"
        "- **Organisational development and structuring:** business regulation and unification; "
        "structuring the organisation for statutory compliance\n"
        "- **Safeguarding:** safeguarding training; instituting a culture of respectful "
        "interactions in the workplace\n"
        "- **Strategy development:** strategic thinking, planning and management; designing "
        "policies, systems and processes",
        "image": "ngo-capacity-development.jpg",
        "image_alt": "Diagram of the five capacity development areas listed beside it",
        "image_on_services_page": True,
        "sort_order": 70,
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


# ---- Services (Day 7) ----------------------------------------------------------------------
# Day 8 adds the enquiry block after the client logos.

SERVICES_META_DESCRIPTION = (
    "Human resources consultancy services: employee relations, NEC services, training, "
    "organisational development, HR audits, restructuring, outsourced HR, talent acquisition, "
    "research surveys and NGO capacity development."
)

SERVICES_SECTIONS: tuple[dict[str, Any], ...] = (
    {
        "anchor": "what-we-do",
        "section_type": "hero_text",
        "heading": "Our Services",
        "body": "At Distinctive Consultancy Services, we specialise in Human Resources "
        "Consultancy Services. Our core business is offering a wide range of strategic "
        "management and specialised and unique Human Resources solutions customised to meet "
        "differing and varying corporate client needs.",
        "sort_order": 10,
    },
    {
        "anchor": "services-list",
        "section_type": "service_bands",
        "heading": "What We Do",
        "sort_order": 20,
    },
    {
        "anchor": "corporate-clients",
        "section_type": "clients",
        "heading": "Some of Our Corporate Clients",
        "heading_align": "center",
        "sort_order": 30,
    },
    {
        "anchor": "get-in-touch",
        "section_type": "enquiry_form",
        "heading": "Get In Touch With Us",
        "heading_align": "center",
        "body": "Tell us what you need and we'll get back to you.",
        "button_label": "Send enquiry",
        "sort_order": 40,
    },
)

CLIENTS: tuple[dict[str, Any], ...] = tuple(
    {"kind": "client", "name": name, "image": image, "image_alt": f"{name} logo", "sort_order": n}
    for n, (name, image) in enumerate(
        (
            ("Zimbabwe Consolidated Diamond Company", "zcdc.png"),
            ("NOIC", "noic.png"),
            ("Reserve Bank of Zimbabwe", "rbz.png"),
            ("TelOne", "telone.png"),
            ("ZIMRA", "zimra.png"),
            ("FBC Holdings Limited", "fbc.png"),
            ("UNDP", "undp.png"),
            ("Bull Red Distribution", "bull-red.png"),
            ("City Parking", "city-parking.png"),
            ("Masimba", "masimba.png"),
        ),
        start=1,
    )
)


# ---- Contact (Day 8) -----------------------------------------------------------------------

CONTACT_META_DESCRIPTION = (
    "Contact Distinctive Consultancy Services at 62 Mutare Road, Msasa, Harare: send us a "
    "message, call +263 (24) 2 486 642 - 3 or email enquiries@distinctive.co.zw."
)

# The address, phone, email, hours and vacancies line come from Site settings, so they are
# edited in one place; the sections hold only the headings and the button.
CONTACT_SECTIONS: tuple[dict[str, Any], ...] = (
    {
        "anchor": "get-in-touch",
        "section_type": "contact_form",
        "heading": "Get In Touch!",
        "button_label": "Submit",
        "sort_order": 10,
    },
    {
        "anchor": "find-us",
        "section_type": "map",
        "heading": "Find Us",
        "sort_order": 20,
    },
)
