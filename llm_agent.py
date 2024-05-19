import openai

class LlmChatAgent:

    def __init__(self, model="gpt-3.5-turbo", api_key=None):
        if api_key:
            print(f"Key : {api_key}")
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.messages = []


    # Function to converse with OpenAI's model
    def converse(self, prompt, max_tokens=4096, temperature=0, top_p=1, frequency_penalty=0, presence_penalty=0):
        self.messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        ).choices[0].message.content
        self.messages.append({"role": "assistant", "content": response})
        return response

    #get messages
    def get_messages(self):
        return self.messages


    # Function to reset the conversation
    def reset(self):
        self.messages = []

    # Function to set the model
    def set_model(self, model):
        self.model = model
        self.reset()

    def list_models(self):
        try:
            models = self.client.models.list()
            model_names = [model.id for model in models.data]
            return model_names
        except Exception as e:
            return None
