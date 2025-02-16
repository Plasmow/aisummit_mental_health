# aisummit_mental_health_hackathon_doctolib
# Loneline: A Supportive AI Chatbot

Welcome to **Loneline** – an AI-powered chatbot designed to help you feel less lonely through engaging, personalized conversations. The chatbot not only provides friendly interaction but also adapts its communication style based on your MBTI personality type, fostering more meaningful and supportive exchanges.

---
-> Launch the app with
 *py flask_app/app.py*

---
## Overview

**Loneline** is inspired by empirical research and expert advice:
- **Group Barkley Experiment & Related Studies**: Our approach is supported by various studies showing the positive effects of social support and peer interaction on mental health. Notable references include:
  - Cohen, S. & Wills, T. A. (1985). *Stress, social support, and the buffering hypothesis*.
  - Holt-Lunstad, J., Smith, T. B. & Layton, J. B. (2010). *Social relationships and mortality risk: a meta-analytic review*.
  - Dennis, C. L. (2003). *Peer support within a health care context: a concept analysis*.
- **Doctor DABOUL's Advice**: Based on clinical experience, Doctor DABOUL emphasizes that people tend to improve when they receive social support. This project is a practical step towards implementing that principle.

The chatbot works by engaging you in conversation to:
1. **Help reduce loneliness** through supportive dialogue.
2. **Determine your MBTI type** after several exchanges.
3. **Adapt its conversational style** to match your MBTI type, ensuring that you interact with a personality that is most compatible with yours.

---

## Features

- **Personalized Conversations**: The AI adapts its tone and conversation style based on the MBTI type it deduces from your interactions.
- **MBTI Compatibility**: After a series of exchanges, the chatbot estimates your MBTI type and adjusts its responses to suit your personality.
- **Moderation System**: A robust moderation system is in place:
  - **Forbidden Words List**: Doctors and moderators can add forbidden words to a `forbidden_words` list, ensuring that discussions remain respectful and free from harmful content.
  - **Thematic Moderation**: In addition to common moderation practices, our system monitors and restricts conversations on pre-defined sensitive topics.
- **Future Feature - Human Matchmaking**: In future releases, a vector similarity program will allow matching users with similar MBTI types, facilitating real-life conversations between people who share compatible traits.
