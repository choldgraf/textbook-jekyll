---
layout: textbook
interact_link: notebooks/12/Comparing_Two_Samples.ipynb
previous:
  url: textbook/11/3/Decisions_and_Uncertainty
  title: '11.3 Decisions and Uncertainty'
next:
  url: textbook/12/1/AB_Testing
  title: '12.1 A/B Testing'
sidebar:
  nav: sidebar-textbook
---

### Comparing Two Samples ###
We have seen several examples of assessing whether a single sample looks like random draws from a specified chance model. 
- Did the Alameda County jury panels look like a random sample from the population of eligible jurors?
- Did the pea plants that Mendel grew have colors that were consistent with the chances he specified in his model?

In all of these cases there was just one random sample, and we were trying to decide how it had been generated. But often, data scientists have to compare two random samples with each other. For example, they might have to compare the outcomes of patients who have been assigned at random to a treatment group and a control group. Or they might have randomized internet users to receive two different versions of a website, after which they would want to compare the actions of the two random groups.

In this chapter, we develop a way of using Python to compare two random samples and answer questions about the similarities and differences between them. You will see that the methods we develop have diverse applications. Our examples are from medicine and public health as well as football!

