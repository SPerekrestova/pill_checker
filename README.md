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
- **Database & Auth:** Using local [Supabase](https://supabase.com) instance for a real-time database and user authentication, making the project fully self-contained and easy to deploy locally.
- **Local Development:** Comprehensive setup instructions and configuration files are provided for easy local deployment and development.
- **AI & NLP:** Leveraging large language models along with pipelines for image text extraction using the [en_ner_bc5cdr_md model from SciSpacy](https://github.com/allenai/scispacy) paired with the [RxNorm linker](https://www.nlm.nih.gov/research/umls/rxnorm/index.html).

## Challenges & Learnings

Building PillChecker was a journey full of learning and experimentation. Here are some hurdles I overcame:
- Building a robust and efficient API with FastAPI to handle medication processing and analysis.
- Integrating image processing and text extraction to reliably scan medicine packs.
- Optimizing performance while managing the heavy memory needs of large language models and smart pipelines.
- Balancing between system performance and resource consumption for local deployment.
- Implementing a real-time database and authentication system using Supabase.

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
