from django.db import models
import openai

# openai.api_key = <your openai apikey>

class FictionFountain(models.Model):
    genre = models.CharField(max_length=20)
    people = models.CharField(max_length=20)
    settings = models.TextField(default='')  # Store generated settings
    outlines = models.TextField(default='')  # Store generated outlines
    chapters = models.TextField(default='[]')  # Store chapters as a JSON-encoded list
    reading_progress = models.IntegerField(default=0)
    next_chapter_id = models.IntegerField(default=1)

    def __str__(self) -> str:
        return f'genre: {self.genre} people: {self.people}'

    def generate_settings(self) -> str:
        # Use OpenAI GPT-3.5 API to generate settings based on genre and people
        role = f'You are a {self.genre} author. Your task is to write {self.genre} stories for {self.people} in a vivid and intriguing language.'
        action = f'Fill out the template below for a {self.genre} story for {self.people}.'
        template = f'''
        Title: [Insert story title here]

        Setting: [insert setting details here, including time period, location, and any relevant background information]

        Protagonist: [Insert protagonist's name, age, and occupation, as well as a brief description of their personality and motivations]

        Antagonist: [Insert antagonist's name, age, and occupation, as well as a brief description of their personality and motivations]

        Conflict: [Insert the main conflict of the story, including the problem the protagonist faces and the stakes involved]

        Dialog: [Instructions for using dialogue to advance the plot, reveal character, and provide information to the reader]

        Theme: [Insert the central theme of the story and instructions for developing it throughout the plot, character, and setting]

        Tone: [Insert the desired tone for the story and instructions for maintaining consistency and appropriateness to the setting and characters]

        Pacing: [Instructions for varying the pace of the story to build and release tension, advance the plot, and create dramatic effect]

        Optional: [insert and additional details or requirements for the story, such as specific word count or genre constraints]
        '''
        prompt = role + action + template
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can choose the appropriate engine
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.7,
        )
        generated_settings = response['choices'][0]['text'].strip()

        # Update the settings field in the model
        self.settings = generated_settings
        self.save()

        return generated_settings

    def generate_chapter(self) -> str:
        # Use the stored settings to generate the first chapter
        genre = self.genre
        people = self.people
        settings = self.settings
        if not settings:
            settings = self.generate_settings()
        next_chapter_id = self.next_chapter_id

        role = f'You are a {genre} author. Your task is to write {genre} stories for {people} in a vivid and intriguing language.'
        prompt = role + f'''
        #### Setting ####
        {settings}'''
        prompt_variation = ""
        previous_outline = self.outlines
        if previous_outline != "":
            prompt += f'''#### Previous Chapters ####
            {previous_outline}
            '''
            prompt_variation = " and Previous Chapters"
        prompt += f'''#### Instruction ####
        Given the Setting{prompt_variation}, build the chapter {next_chapter_id} outline with following format:
        #### format ####
        Chapter {next_chapter_id}
        event 1
        event 2
        event ...
        '''
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can choose the appropriate engine
            prompt=prompt,
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.7,
        )
        chapter_outline = response['choices'][0]['text'].strip()
        previous_outline += "\n" + chapter_outline
        self.outlines = previous_outline

        prompt = f'''
        {role}
        #### setting ####
        {settings}
        #### chapter outlines ####
        {previous_outline} 
        #
        '''
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can choose the appropriate engine
            prompt=prompt,
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.7,
        )
        chapter = response['choices'][0]['text'].strip()
        
        # Append to self.chapters
        chapters_list = self.get_chapters_list()
        chapters_list.append(chapter)
        self.chapters = chapters_list
        
        next_chapter_id += 1
        self.next_chapter_id = next_chapter_id
        self.save()
        return chapter

    def get_chapters_list(self):
        import json
        return json.loads(self.chapters)
