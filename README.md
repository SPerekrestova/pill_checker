# PillChecker: Medication Intersection Project

Welcome to PillChecker – a project born out of my love for coding and healthcare. This is my playground for learning new tech, experimenting with AI, and solving real-world challenges.

## Project Overview

PillChecker is designed to simplify the process of managing medication interactions. Instead of rummaging through instructions or searching online, this project aims to provide a straightforward solution.

## Idea & Purpose

The concept behind PillChecker is straightforward. Imagine you need a painkiller but are already taking other medications. PillChecker helps ensure safety by managing and checking medication interactions.

## Tech Stack & Tools

- **Language:** Python
- **Web Frameworks:**
  - [Django](https://www.djangoproject.com)
  - [Flask](https://flask.palletsprojects.com)
  - [FastAPI](https://fastapi.tiangolo.com)
- **Containerization:** [Docker](https://www.docker.com)
- **Cloud Hosting:** Started with AWS, then switched to [DigitalOcean](https://www.digitalocean.com) for cost-effectiveness.
- **Database & Auth:** Using [Supabase](https://supabase.com) for a real-time database and user authentication.
- **AI & NLP:** Leveraging large language models along with pipelines for image text extraction using the [en_ner_bc5cdr_md model from SciSpacy](https://github.com/allenai/scispacy) paired with the [RxNorm linker](https://www.nlm.nih.gov/research/umls/rxnorm/index.html).

## Frontend UI

The user interface is a vital part of PillChecker. This sleek, user-friendly interface is crafted by [Dan K.](https://github.com/dankrasilnikov).

## Challenges & Learnings

Building PillChecker was a journey full of learning and experimentation. Here are some hurdles I overcame:
- Switching between different Python frameworks to build a full-featured web app and API.
- Integrating image processing and text extraction to reliably scan medicine packs.
- Optimizing performance while managing the heavy memory needs of large language models.
- Experimenting with cloud deployment and containerization.
- Implementing a real-time database and authentication system using Supabase.

## Future Enhancements

There’s plenty more on the horizon! Here’s what I’m planning next:
- **Interaction Analysis:** Real-time checks for drug interactions with detailed trademark resolution.
- **Resource Optimization:** Fine-tuning deployment to handle memory and processing demands better.
- **Feature Expansion:** Adding personalized medication recommendations and smarter alerts.
- **Advanced AI Techniques:** Exploring improved OCR and NLP methods.

## Links & Acknowledgments

A huge thanks to [Dan K.](https://github.com/dankrasilnikov) for the UI part and [Hiddenmarten](https://github.com/hiddenmarten) for the whole DevOps support!

Check out the tools I used:
- [SciSpacy (en_ner_bc5cdr_md model)](https://github.com/allenai/scispacy)
- [RxNorm Linker](https://www.nlm.nih.gov/research/umls/rxnorm/index.html)
- [World Health Organization](https://www.who.int)

## Conclusion

PillChecker reflects my passion for both healthcare and tech. It’s a hands-on example of how quickly you can learn a new tech stack and build something that truly makes a difference.

## **License**  

This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for details.  