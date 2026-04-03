want you to create a POC for a mini project internal too to
  schedule classes for student for different course....


Tech stack: Frontend React+VIte+tailwind

[tailwind instructions Installing Tailwind CSS as a Vite plugin is the most seamless way to integrate it with frameworks like Laravel, SvelteKit, React Router, Nuxt, and SolidJS.

01
Create your project
Start by creating a new Vite project if you don’t have one set up already. The most common approach is to use Create Vite.

Terminal

npm create vite@latest my-project
cd my-project
02
Install Tailwind CSS
Install tailwindcss and @tailwindcss/vite via npm.

Terminal

npm install tailwindcss @tailwindcss/vite
03
Configure the Vite plugin
Add the @tailwindcss/vite plugin to your Vite configuration.

vite.config.ts

import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
export default defineConfig({
  plugins: [
    tailwindcss(),
  ],
})
04
Import Tailwind CSS
Add an @import to your CSS file that imports Tailwind CSS.

CSS

@import "tailwindcss";
05
Start your build process
Run your build process with npm run dev or whatever command is configured in your package.json file.

Terminal

npm run dev
06
Start using Tailwind in your HTML
Make sure your compiled CSS is included in the <head> (your framework might handle this for you), then start using Tailwind’s utility classes to style your content.

HTML

<!doctype html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="/src/style.css" rel="stylesheet">
</head>
<body>
  <h1 class="text-3xl font-bold underline">
    Hello world!
  </h1>
</body>
</html>]


Backend FastAPI + uv+uvicorn [no datbase only in memory data for now]

the main idea is i want a calender like view in the frontend in which user is able to perform CRUD operations on classes for various courses...they should be able to select the class topic name, the assignment name...the date the start time [each class is always 1.5hrs]

this class create a respective zoom meeting in the zoom video conferencing platform.
and on editing the details in the frontend also updates the deetails in the zoom meeting....the zoom meeing id and link should also be saved along with the scheduled class

regarding this i want you to create a simple architechture doc and ask any clarification questions that you have

