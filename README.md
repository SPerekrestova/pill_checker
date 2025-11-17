# PillChecker: Medication Intersection Project

Welcome to PillChecker – a project born out of my love for coding and healthcare. This is my playground for learning new tech, experimenting with AI, and solving real-world challenges in the healthcare domain. Whether you're a developer or just curious about how tech can make medicine safer, you'll find plenty to explore here.

## Project Overview

PillChecker is designed to simplify the process of managing medication interactions. Instead of rummaging through endless instructions or searching online, you snap a quick picture of the medicine pack. The app then extracts key details like the trademark, dosage, and active ingredients and checks them against trusted medical info to ensure there's no risk of dangerous interactions.

## Idea & Purpose

The concept behind PillChecker is straightforward. Imagine you need a painkiller but are already taking other medications. Instead of rummaging through endless instructions or searching online, you snap a quick picture of the medicine pack. The app then extracts key details like the trademark, dosage, and active ingredients and checks them against trusted medical info to ensure there's no risk of dangerous interactions.

This project is not just a tech challenge – it's a passion project that shows how software can directly improve healthcare safety.

## Tech Stack & Tools

- **Language:** Python
- **Web Framework:** [FastAPI](https://fastapi.tiangolo.com) - chosen for its lightweight nature and simplicity
- **Containerization:** [Docker](https://www.docker.com)
- **Cloud Hosting:** Currently running locally, with cloud deployment planned for the future once resource optimization is achieved.
- **Database:** PostgreSQL with [SQLAlchemy](https://www.sqlalchemy.org/) ORM for robust data management
- **Authentication:** [FastAPI-Users](https://fastapi-users.github.io/fastapi-users/) for secure JWT-based authentication
- **Storage:** Local filesystem-based storage for medication scans with plans for cloud integration
- **Local Development:** Comprehensive setup instructions and configuration files are provided for easy local deployment and development.
- **AI & NLP:** Leveraging [BiomedNER](https://github.com/YOUR_REPO/biomed-ner) for medical entity recognition along with pipelines for image text extraction using OCR technology.

## Challenges & Learnings

Building PillChecker was a journey full of learning and experimentation. Here are some hurdles I overcame:
- Building a robust and efficient API with FastAPI to handle medication processing and analysis.
- Integrating image processing and text extraction to reliably scan medicine packs.
- Optimizing performance while managing the heavy memory needs of large language models and smart pipelines.
- Balancing between system performance and resource consumption for local deployment.
- Implementing custom authentication with FastAPI-Users and migrating from Supabase to a fully self-managed solution.
- Designing a scalable storage system that can transition from local filesystem to cloud storage.

## Future Enhancements

There's plenty more on the horizon! Here's what I'm planning next:
- **Cloud Deployment:** Implementing cloud hosting solution once resource optimization and cost-effectiveness are achieved.
- **Resource Optimization:** Fine-tuning the system to handle memory and processing demands of NLP models more efficiently.
- **Interaction Analysis:** Rolling out real-time checks for drug interactions with even more detailed trademark resolution.
- **Feature Expansion:** Adding personalized medication recommendations and smarter alerts by integrating additional health databases.
- **Advanced AI Techniques:** Exploring improved OCR and NLP methods to speed up and refine text extraction.

## Links & Acknowledgments

A huge thanks to [Hiddenmarten](https://github.com/hiddenmarten) for the whole DevOps support!

Check out the tools I used:
- [SciSpacy (en_ner_bc5cdr_md model)](https://github.com/allenai/scispacy)
- [RxNorm Linker](https://www.nlm.nih.gov/research/umls/rxnorm/index.html)
- [World Health Organization](https://www.who.int)

## Conclusion

PillChecker is a project that reflects my passion for both healthcare and tech. It's a hands-on example of how quickly you can learn a new tech stack and build something that truly makes a difference. I hope this project inspires others to explore innovative ways to bridge the gap between technology and healthcare.

## License

This project is licensed under the GPL-3.0 license.
