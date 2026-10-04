\# Poshan AI



AI-assisted child nutrition screening support system for rural healthcare workers.



\## Project Overview



Poshan AI is a software-based prototype designed to support Anganwadi and ASHA workers with child nutrition screening.



The system combines:

\- Child age, sex, height and weight

\- WHO Child Growth Standards reference data

\- Computer-vision-based image quality analysis

\- Screening-priority generation

\- A clear medical disclaimer



The prototype is designed as decision-support software and does not replace clinical evaluation.



\## Person 4 — Computer Vision + Health Analysis



The Person 4 module handles:



1\. Child image upload

2\. Image quality analysis

3\. Brightness and contrast analysis

4\. Image clarity estimation

5\. Lighting-uniformity analysis

6\. RGB/color analysis

7\. WHO-based height and weight reference-band screening

8\. Overall screening priority

9\. Frontend-ready screening summary



\## Current Computer Vision Capabilities



The current local prototype performs non-medical image analysis including:



\- Resolution

\- Brightness

\- Contrast

\- Clarity

\- Lighting uniformity

\- RGB channel statistics

\- Color information



Medical visual indicators such as pallor or rib prominence are currently marked as not assessed because a validated medical visual-AI model is not connected.



\## Growth Screening



The prototype uses locally stored WHO Child Growth Standards reference files for available age ranges.



The current implementation provides reference-band screening for:

\- Height-for-age

\- Weight-for-age



This is a reference-band screening implementation and should not be interpreted as a clinical diagnosis or a complete WHO z-score calculation.



\## Running the Project



Create and activate the virtual environment:



```powershell

python -m venv venv

.\\venv\\Scripts\\activate

