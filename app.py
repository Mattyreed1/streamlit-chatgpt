import openai
import streamlit as st
from streamlit_chat import message
from PIL import Image

# Setting page title
st.set_page_config(page_title="LifeAlign", page_icon=":robot_face:")

# Setting the logo header
# opening the logo image
image = Image.open('images/ta-logo.png')
#displaying the image in center on streamlit app
col1, col2, col3 = st.columns(3)

with col1:
    st.write(' ')

with col2:
    st.image(image, width=200)

with col3:
    st.write(' ')

# Setting the header
st.markdown("<h1 style='text-align: center;'>Chat with your LifeAlign Coach</h1>", unsafe_allow_html=True)

# Set API Key
openai.api_key = st.secrets.openai_api_key

# Set org ID and API key
#openai.organization = "<OPENAI_ORG_ID>"

# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0

# Sidebar - let user choose model, show total cost of current conversation, and let user clear the current conversation
st.sidebar.title("Sidebar")
model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
counter_placeholder = st.sidebar.empty()
counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
clear_button = st.sidebar.button("Clear Conversation", key="clear")

# Map model names to OpenAI model IDs
if model_name == "GPT-3.5":
    model = "gpt-3.5-turbo"
else:
    model = "gpt-4"

# reset everything
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.session_state['number_tokens'] = []
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []
    counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")


# generate a response
def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})
    print(prompt)

    completion = openai.ChatCompletion.create(
        model=model,
        messages=st.session_state['messages']
    )
    response = completion.choices[0].message.content
    st.session_state['messages'].append({"role": "assistant", "content": response})

    # print(st.session_state['messages'])
    total_tokens = completion.usage.total_tokens
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    return response, total_tokens, prompt_tokens, completion_tokens


# container for chat history
response_container = st.container()
# container for text box
container = st.container()

initial_prompt = """Please think and speak like an experienced life coach and talk to me like I’m your client.

Your objective is to help me clarify and quantify my goal into a measurable metric, then create calendar time blocks (in a .ics file) that I can import into my calendar.

You should help me decide on a specific deadline to achieve my goal, then help break the goal down into specific tasks and activities that can be converted into time blocks on my calendar. You should also help me clarify exactly how I can measure progress towards this goal.

In order to help me clarify and quantify my goal, you should ask me clarifying questions and continue asking clarifying questions until the goal is more concrete, ideally with a deadline, a measurable metric, and actionable steps that can be scheduled. Please search the web and link to specific resources that would be useful to better understand and measure my progress.

You should also ask questions to better understand my motivation. If my goal is unrealistic or too difficult, you should give recommendations based on the best life coach advice you are aware of. When possible, refer to research and scientific studies that support your advice.

Ask questions about the names of any people that I mention (then use the names when referring to them), and try to ask questions to make sure I’m being specific about whatever it is we are talking about.

Every question you ask me should have a number so I can easily respond to the question.

FOR EXAMPLE: I say my goal is to “lose weight”, You should ask a clarifying question such as: “How much do you weigh now and how much do you want to weigh?” You should ask a question like, “Have you tried any diets or weight loss medication in the past? What were they specifically?” Then you might ask something like, “When do you want to lose this weight by?” And if my answer is unrealistic, you should respond with something like, "Typically, it takes 1 month to lose 20lbs, therefore, I recommend you choose a deadline at least 2 months from now.” You should clarify exactly how I will measure progress towards my goal by asking things like, “Do you have a scale?” And if I don’t have a scale, you should respond with a link to a highly rated and affordable scale that I can purchase and delivered to my house from Amazon or my favorite online marketplace. You should also ask clarifying questions to better understand my motivation, such as, “Why do you want to lose weight?” or “How will losing weight improve your wellbeing?” or “Will you be more fulfilled if you lose weight? Why is that?”

Remember, your objective is to help me take my vague goal and convert it into scheduled time blocks on my calendar. Once you are clear enough about the time blocks that need to be scheduled to achieve my goal, please export .ICS code (iCalendar universal calendar file) that can be imported directly into a Google Calendar. The event title and description should include all relevant information and any other event parameters that are important.

"""


with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['model_name'].append(model_name)
        st.session_state['total_tokens'].append(total_tokens)

        # from https://openai.com/pricing#language-models
        if model_name == "GPT-3.5":
            cost = total_tokens * 0.002 / 1000
        else:
            cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000

        st.session_state['cost'].append(cost)
        st.session_state['total_cost'] += cost

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
            st.write(
                f"Model used: {st.session_state['model_name'][i]}; Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}")
            counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
