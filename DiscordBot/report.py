from enum import Enum, auto
import discord
import re

class State(Enum):
    REPORT_START = auto()
    AWAITING_MESSAGE = auto()
    MESSAGE_IDENTIFIED = auto()
    REPORT_CONFIRM = auto()

    SCAM = auto()
    HARASSMENT = auto()
    VIOLENCE = auto()
    CATEGORY_OTHER = auto()

    # dating scam
    REPORT_CONTINUE = auto()
    REPORT_ELABORATION = auto()
    REPORT_ELABORATION_YESNO = auto()
    AWAIT_REPORT = auto()
    NEXT_STEP = auto()

    # harassment
    AWAIT_USERNAME = auto()
    SELECT_HARASSMENT_TYPE = auto()
    AWAIT_HARASSMENT_TYPE = auto()

    # violence
    REPORT_VIOLENCE = auto()
    AWAIT_USERNAME_VIOLENCE = auto()

    # other
    AWAIT_REPORT_OTHER = auto()
    NEXT_STEP_OTHER = auto()

    REPORT_COMPLETE = auto()

class Report:
    START_KEYWORD = "report"
    CANCEL_KEYWORD = "cancel"
    HELP_KEYWORD = "help"

    def __init__(self, client):
        self.state = State.REPORT_START
        self.client = client
        self.message = None

        # report details
        self.user = ""  # the user that is experiencing the scam / harassment / violence
        self.report_category = ""
        self.report_content = ""
        self.message_link = ""
        # self.report_subcategory = ""
        self.report_description = ""
    
    async def handle_message(self, message):
        '''
        This function makes up the meat of the user-side reporting flow. It defines how we transition between states and what 
        prompts to offer at each of those states. You're welcome to change anything you want; this skeleton is just here to
        get you started and give you a model for working with Discord. 
        '''

        if message.content == self.CANCEL_KEYWORD:
            self.state = State.REPORT_COMPLETE
            return ["Report cancelled."]
        
        if self.state == State.REPORT_START:
            reply =  "Thank you for starting the reporting process. "
            reply += "Say `help` at any time for more information.\n\n"
            reply += "Please copy paste the link to the message you want to report.\n"
            reply += "You can obtain this link by right-clicking the message and clicking `Copy Message Link`."
            self.state = State.AWAITING_MESSAGE
            return [reply]
        
        if self.state == State.AWAITING_MESSAGE:
            # Parse out the three ID strings from the message link
            m = re.search('/(\d+)/(\d+)/(\d+)', message.content)
            if not m:
                return ["I'm sorry, I couldn't read that link. Please try again or say `cancel` to cancel."]
            guild = self.client.get_guild(int(m.group(1)))
            if not guild:
                return ["I cannot accept reports of messages from guilds that I'm not in. Please have the guild owner add me to the guild and try again."]
            channel = guild.get_channel(int(m.group(2)))
            if not channel:
                return ["It seems this channel was deleted or never existed. Please try again or say `cancel` to cancel."]
            try:
                message = await channel.fetch_message(int(m.group(3)))
            except discord.errors.NotFound:
                return ["It seems this message was deleted or never existed. Please try again or say `cancel` to cancel."]

            # Here we've found the message - it's up to you to decide what to do next!
            self.state = State.MESSAGE_IDENTIFIED
            self.report_content = message.content
            self.message_link = message.jump_url
            return ["I found this message:", "```" + message.author.name + ": " + message.content + "```", \
                    "If this is the message you'd like to report, please confirm by typing `report`, otherwise, you can cancel the report by saying `cancel`."]
        
        if self.state == State.MESSAGE_IDENTIFIED:
            self.state = State.REPORT_CONFIRM
            reply = "Select a problem with this message. The sender will not be notified of this report.\n"
            reply += "Choose from the following categories [``scam/fraud``, ``harassment``, ``violence``, ``other``]"
            return [reply]
        
        # User selecting categories
        if self.state == State.REPORT_CONFIRM:
            if message.content == "scam/fraud":
                self.state = State.SCAM
                self.report_category = "scam/fraud"
                reply = "Please select the type of fraud you would like to report.\n"
                reply += "``phishing``, ``impersonation``, ``cryptocurrency``, ``dating scam``, ``other``"
            elif message.content == "harassment":
                self.state = State.HARASSMENT
                self.report_category = "harassment"
                reply = "Who is the harassment directed towards?\n"
                reply += "Please select ``myself`` or ``someone I know``.`"
            elif message.content == "violence":
                self.state = State.VIOLENCE
                self.report_category = "violence"
                reply = "Who is the violence directed towards?\n"
                reply += "Please select ``myself`` or ``someone I know``."
            elif message.content == "other":
                self.state = State.CATEGORY_OTHER
                self.report_category = "other"
                reply = "We are committed to upholding our community standard and your input is valuable to us. Would you like to elaborate on your report?\n"
                reply += "Please select ``yes`` or ``no``."
            else:
                reply = "I'm sorry, I couldn't read that message. Please try again or say `cancel` to cancel."

            return [reply]
        
        # User selected scam/fraud category
        if self.state == State.SCAM:
            if message.content == "phishing" or \
               message.content == "impersonation" or \
               message.content == "cryptocurrency":
                self.state = State.REPORT_COMPLETE
                return ["Thank you for your report. A moderator will follow up on it."]
            elif message.content == "dating scam":
                reply = "We define dating/ romance scams as the criminal act of feigning a romantic relationship in order to extort, manipulate, or otherwise financially benefit from another person.\n"
                reply += "Would you like to continue with your report?\n"
                reply += "Please select [``yes`` or ``no``]."
                self.state = State.REPORT_CONTINUE
                return [reply]
            elif message.content == "other":
                self.state = State.REPORT_ELABORATION
            else:
                return ["I'm sorry, I couldn't read that message. Please try again or say `cancel` to cancel."]
        if self.state == State.REPORT_CONTINUE:
            if message.content == "yes": 
                self.state = State.REPORT_ELABORATION
            elif message.content == "no":
                return
            else:
                return ["I'm sorry, I couldn't read that message. Please try again or say `cancel` to cancel."]
        
        # User selected harassment category
        if self.state == State.HARASSMENT:
            if message.content == "myself":
                self.user = message.author.id   # store as the message author
                self.state = State.SELECT_HARASSMENT_TYPE
            elif message.content == "someone I know":
                self.state = State.AWAIT_USERNAME
                return ["Please provide their username."]
            else:
                return ["I'm sorry, I couldn't read that message. Please try again or say `cancel` to cancel."]
        if self.state == State.AWAIT_USERNAME:
            self.user = message.content
            self.state = State.SELECT_HARASSMENT_TYPE
        if self.state == State.SELECT_HARASSMENT_TYPE:
            reply = "What type of harassment is it?\n"
            reply += "Please select from [``bullying``, ``hate speech``, ``sexual content``, ``other``]"
            self.state = State.AWAIT_HARASSMENT_TYPE
            return [reply]
        if self.state == State.AWAIT_HARASSMENT_TYPE:
            if message.content == "bullying" or \
            message.content == "hate speech" or \
            message.content == "sexual content" or \
            message.content == "other":
                self.state = State.REPORT_ELABORATION
            else:
                return ["I'm sorry, I couldn't read that message. Please try again or say `cancel` to cancel."]
        
        # Report elaboration for both scam/fraud and harassment categories
        if self.state == State.REPORT_ELABORATION:
            reply = "Would you like to elaborate on your report?\n"
            reply += "Please select [``yes`` or ``no``]."
            self.state = State.REPORT_ELABORATION_YESNO
            return [reply]  
        if self.state == State.REPORT_ELABORATION_YESNO:
            if message.content == "yes":
                reply = "Please provide the description."
                self.state = State.AWAIT_REPORT
                return [reply]
            elif message.content == "no":
                self.state = State.NEXT_STEP
        if self.state == State.AWAIT_REPORT:
            self.report_description = message.content   # store user report message
            self.state = State.NEXT_STEP
        if self.state == State.NEXT_STEP:
            reply = "Thank you.Your report has been submitted. Our moderators will conduct an investigation and determine whether the content violates our Community Guidelines. If this is an emergency, please contact your local authorities.\n"
            # reply += "Would you like to prevent any further contact by blocking this user and any future accounts they may create?\n"
            # reply += "Please select [``no``, ``this user only``, ``this user and future accounts``]"
            # TODO: add subsequent moderator actions after moderator flow
            self.state = State.REPORT_COMPLETE
            return [reply]

        # User selected violence category
        if self.state == State.VIOLENCE:
            if message.content == "myself":
                self.user = message.author.id   # store as the message author
                self.state = State.REPORT_VIOLENCE
            elif message.content == "someone I know":
                self.state = State.AWAIT_USERNAME_VIOLENCE
                return ["Please provide their username."]
            else:
                return ["I'm sorry, I couldn't read that message. Please try again or say `cancel` to cancel."]
        if self.state == State.AWAIT_USERNAME_VIOLENCE:
            self.user = message.content
            self.state = State.REPORT_VIOLENCE
        if self.state == State.REPORT_VIOLENCE:
            self.state = State.REPORT_COMPLETE
            return ["Thank you. Your report has been submitted. Our moderators will conduct an investigation and determine whether the content violates our Community Guidelines. If this is an emergency, please contact your local authorities."]


        # User selected other category
        if self.state == State.CATEGORY_OTHER:
            if message.content == "yes":
                reply = "Please provide the description."
                self.state = State.AWAIT_REPORT_OTHER
                return [reply]
            elif message.content == "no":
                self.state = State.NEXT_STEP_OTHER
        if self.state == State.AWAIT_REPORT_OTHER:
            self.report_description = message.content   # store user report message
            self.state = State.NEXT_STEP_OTHER
        if self.state == State.NEXT_STEP_OTHER:
            self.state = State.REPORT_COMPLETE
            return ["Thank you. Your report has been submitted. Our moderators will conduct an investigation and determine whether the content violates our Community Guidelines. If this is an emergency, please contact your local authorities."]

        return []

    def report_complete(self):
        return self.state == State.REPORT_COMPLETE
    


    

