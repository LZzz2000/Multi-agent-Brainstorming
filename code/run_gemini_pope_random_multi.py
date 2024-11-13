import os
import json
import random
# random.seed(0)
# from code.utils.agent import Agent
from agent_gemini import Agent
import tqdm
import sys

gemini_api_key = ""

NAME_LIST = [
    "Player 1",
    "Player 2",
    "Moderator",
]

questions_file = open("../data/coco_pope_random.json", "r")
out_file = ""
role = True
A_artifical = True

class DebatePlayer(Agent):
    def __init__(self, model_name: str, name: str, temperature: float, gemini_api_key: str, sleep_time: float) -> None:
        """Create a player in the debate

        Args:
            model_name(str): model name
            name (str): name of this player
            temperature (float): higher values make the output more random, while lower values make it more focused and deterministic
            gemini_api_key (str): As the parameter name suggests
            sleep_time (float): sleep because of rate limits
        """
        super(DebatePlayer, self).__init__(model_name, name, gemini_api_key, temperature, sleep_time, )
        self.gemini_api_key = gemini_api_key


class Debate:
    def __init__(self,
                 model_name: str = 'gemini-1.5-flash',
                 temperature: float = 0,
                 num_players: int = 3,
                 gemini_api_key: str = None,
                 config: dict = None,
                 max_round: int = 5,
                 sleep_time: float = 0,
                 img: str = None,
                 discussion_process: str = None,
                 history: dict = None
                 ) -> None:
        """Create a debate

        Args:
            model_name (str): gemini model name
            temperature (float): higher values make the output more random, while lower values make it more focused and deterministic
            num_players (int): num of players
            gemini_api_key (str): As the parameter name suggests
            max_round (int): maximum Rounds of Debate
            sleep_time (float): sleep because of rate limits
        """

        self.model_name = model_name
        self.temperature = temperature
        self.num_players = num_players
        self.gemini_api_key = gemini_api_key
        self.config = config
        self.max_round = max_round
        self.sleep_time = sleep_time
        self.img = img
        self.discussion_process = discussion_process
        self.history = history

        self.init_prompt()

        # creat&init agents
        self.creat_agents()
        self.init_agents()

    def init_prompt(self):
        def prompt_replace(key):
            self.config[key] = self.config[key].replace("##discussion_topic##", self.config["debate_topic"])

        prompt_replace("player_meta")
        prompt_replace("moderator_meta")
        prompt_replace("player_answer1")
        prompt_replace("moderator_question")
        prompt_replace("judge_meta")

    def creat_agents(self):
        # creates players
        self.players = [
            DebatePlayer(model_name=self.model_name, name=name, temperature=self.temperature,
                         gemini_api_key=self.gemini_api_key, sleep_time=self.sleep_time) for name in NAME_LIST
        ]
        self.player1 = self.players[0]
        self.player2 = self.players[1]
        self.moderator = self.players[2]

    def init_agents(self):
        # start: set meta prompt
        self.player1.set_meta_prompt(self.config['player_meta'], self.img)
        self.player2.set_meta_prompt(self.config['player_meta'], self.img)
        self.moderator.set_meta_prompt(self.config['moderator_meta'], self.img)

        if role:
            self.player1.add_event(self.config['imaginative_role'])
            self.player1.ask(self.config['imaginative_role'])
            self.player2.add_event(self.config['conservative_role'])
            self.player2.ask(self.config['conservative_role'])

        # start: first round debate, state opinions

        print(f"===== Debate Round-1 =====\n")
        self.discussion_process += "===== Debate Round-1 =====\n"
        self.player1.add_event(self.config['player_answer1'])
        self.player1_ans = self.player1.ask(self.config['player_answer1'])
        self.player1.add_memory(self.player1_ans)

        self.discussion_process += f"----- Player 1 -----\n{self.player1_ans}\n"
        self.config['base_answer'] = self.player1_ans

        self.player2.add_event(self.config['player_answer1'])
        self.player2_ans = self.player2.ask(self.config['player_answer1'])
        self.player2.add_memory(self.player2_ans)

        self.discussion_process += f"----- Player 2 -----\n{self.player2_ans}\n"

        self.history["Round 1"] = [
            {
                "Role": "Player 1",
                "Question": self.config["debate_topic"],
                "Answer": self.player1_ans
            },
            {
                "Role": "Player 2",
                "Question": self.config["debate_topic"],
                "Answer": self.player2_ans
            }
        ]

        self.moderator.add_event(self.config['moderator_summarize'].replace("##discussion_history##", json.dumps(self.history)))
        self.moderator_summary = self.moderator.ask(self.config['moderator_summarize'].replace("##discussion_history##", json.dumps(self.history)))
        self.moderator.add_memory(self.moderator_summary)

        self.discussion_process += f"----- Moderator -----\n{self.moderator_summary}\n"

        self.moderator.add_event(self.config['moderator_question'].replace("##moderator_summary##", self.moderator_summary).replace(
                "##which_side##", "Player 1").replace("##round_num##", "first")
            )
        self.moderator_ans = self.moderator.ask(self.config['moderator_question'].replace("##moderator_summary##", self.moderator_summary).replace(
                "##which_side##", "Player 1").replace("##round_num##", "first")).strip('```json').strip('```')
        self.moderator.add_memory(self.moderator_ans)

        self.discussion_process += f"----- Moderator -----\n{self.moderator_ans}\n"
        self.moderator_ans = eval(self.moderator_ans)

    def round_dct(self, num: int):
        dct = {
            1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth', 6: 'sixth', 7: 'seventh', 8: 'eighth',
            9: 'ninth', 10: 'tenth'
        }
        return dct[num]

    def print_answer(self):
        print("\n\n===== Debate Done! =====")
        print("\n----- Debate Topic -----")
        print(self.config["debate_topic"])
        print("\n----- Base Answer -----")
        print(self.config["base_answer"])
        print("\n----- Debate Answer -----")
        print(self.config["debateAnswer"])
        print("\n----- Debate Reason -----")
        print(self.config["Reason"])

        self.discussion_process += "\n\n===== Debate Done! ====="
        self.discussion_process += "\n----- Debate Topic -----"
        self.discussion_process += self.config["debate_topic"]
        self.discussion_process += "\n----- Base Answer -----"
        self.discussion_process += self.config["base_answer"]
        self.discussion_process += "\n----- Debate Answer -----"
        self.discussion_process += self.config["debateAnswer"]
        self.discussion_process += "\n----- Debate Reason -----"
        self.discussion_process += self.config["Reason"]


        # print(self.player1.memory_lst)
        # print(self.player2.memory_lst)
        # print(self.moderator.memory_lst)

    def broadcast(self, msg: str):
        """Broadcast a message to all players.
        Typical use is for the host to announce public information

        Args:
            msg (str): the message
        """
        # print(msg)
        for player in self.players:
            player.add_event(msg)

    def speak(self, speaker: str, msg: str):
        """The speaker broadcast a message to all other players.

        Args:
            speaker (str): name of the speaker
            msg (str): the message
        """
        if not msg.startswith(f"{speaker}: "):
            msg = f"{speaker}: {msg}"
        # print(msg)
        for player in self.players:
            if player.name != speaker:
                player.add_event(msg)

    def ask_and_speak(self, player: DebatePlayer):
        ans = player.ask(self.img)
        player.add_memory(ans)
        self.speak(player.name, ans)

    def run(self):

        for round in range(self.max_round - 1):
            if A_artifical:
                self.moderator_ans["Questions"].append("Now, please answer the discussion topic again: "+ "\""+self.config["debate_topic"]+"\"")

            if self.moderator_ans["Whether there is a consensus"] == "Yes":
                break
            else:
                print(f"===== Debate Round-{round + 2} =====\n")
                self.discussion_process += f"===== Debate Round-{round + 2} =====\n"

                if (round + 2) % 2 == 0:
                    self.player1.add_event(self.config['player_answer2'].replace("##moderator_summary##", self.moderator_summary).replace("##moderator_questions##", str(self.moderator_ans["Questions"])))
                    self.player1_ans = self.player1.ask(self.config['player_answer2'].replace("##moderator_summary##", self.moderator_summary).replace(
                            "##moderator_questions##", str(self.moderator_ans["Questions"]))).strip('```json').strip('```')
                    self.player1.add_memory(self.player1_ans)

                    self.discussion_process += f"----- Player 1 -----\n{self.player1_ans}\n"
                    self.player1_ans = eval(self.player1_ans)

                    self.history[f"Round {round + 2}"] = []
                    for kk in range(len(self.player1_ans["Answers"])):
                        self.history[f"Round {round + 2}"].append(
                            {
                                "Role": "Player 1",
                                "Question": self.player1_ans["Answers"][kk]["Question"],
                                "Answer": self.player1_ans["Answers"][kk]["Answer"]
                            }
                        )

                    self.moderator.add_event(self.config['moderator_summarize'].replace("##discussion_history##", json.dumps(self.history)))
                    self.moderator_summary = self.moderator.ask(self.config['moderator_summarize'].replace("##discussion_history##", json.dumps(self.history)))

                    self.discussion_process += f"----- Moderator -----\n{self.moderator_summary}\n"

                    self.moderator.add_memory(self.moderator_summary)

                    self.moderator.add_event(self.config['moderator_question'].replace("##moderator_summary##",self.moderator_summary).replace("##which_side##", "Player 2").replace("##round_num##", self.round_dct(round + 2)))
                    self.moderator_ans = self.moderator.ask(self.config['moderator_question'].replace("##moderator_summary##",self.moderator_summary).replace("##which_side##", "Player 2").replace("##round_num##", self.round_dct(round + 2))).strip('```json').strip('```')

                    self.discussion_process += f"----- Moderator -----\n{self.moderator_ans}\n"

                    self.moderator.add_memory(self.moderator_ans)
                    self.moderator_ans = eval(self.moderator_ans)

                else:
                    self.player2.add_event(self.config['player_answer2'].replace("##moderator_summary##", self.moderator_summary).replace("##moderator_questions##", str(self.moderator_ans["Questions"])))
                    self.player2_ans = self.player2.ask(self.config['player_answer2'].replace("##moderator_summary##", self.moderator_summary).replace("##moderator_questions##", str(self.moderator_ans["Questions"]))).strip('```json').strip('```')
                    self.player2.add_memory(self.player2_ans)

                    self.discussion_process += f"----- Player 2 -----\n{self.player2_ans}\n"
                    self.player2_ans = eval(self.player2_ans)

                    self.history[f"Round {round + 2}"] = []
                    for kk in range(len(self.player2_ans["Answers"])):
                        self.history[f"Round {round + 2}"].append(
                            {
                                "Role": "Player 2",
                                "Question": self.player2_ans["Answers"][kk]["Question"],
                                "Answer": self.player2_ans["Answers"][kk]["Answer"]
                            }
                        )

                    self.moderator.add_event(self.config['moderator_summarize'].replace("##discussion_history##", json.dumps(self.history)))
                    self.moderator_summary = self.moderator.ask(self.config['moderator_summarize'].replace("##discussion_history##", json.dumps(self.history)))

                    self.discussion_process += f"----- Moderator -----\n{self.moderator_summary}\n"

                    self.moderator.add_memory(self.moderator_summary)

                    self.moderator.add_event(self.config['moderator_question'].replace("##moderator_summary##",self.moderator_summary).replace("##which_side##", "Player 1").replace("##round_num##", self.round_dct(round + 2)))
                    self.moderator_ans = self.moderator.ask(self.config['moderator_question'].replace("##moderator_summary##",self.moderator_summary).replace("##which_side##", "Player 1").replace("##round_num##", self.round_dct(round + 2))).strip('```json').strip('```')

                    self.discussion_process += f"----- Moderator -----\n{self.moderator_ans}\n"

                    self.moderator.add_memory(self.moderator_ans)
                    self.moderator_ans = eval(self.moderator_ans)

        if self.moderator_ans["Whether there is a consensus"] == "Yes":
            self.config["Reason"] = self.moderator_ans["Reason"]
            self.config["debateAnswer"] = self.moderator_ans["Ultimate answer of the discussion topic"]
            self.print_answer()
        else:
            self.moderator.add_event(self.config['judge_meta'].replace("##moderator_summary##", self.moderator_summary))
            self.moderator_ans = self.moderator.ask(self.config['judge_meta'].replace("##moderator_summary##", self.moderator_summary)).strip('```json').strip('```')
            self.moderator.add_memory(self.moderator_ans)

            self.discussion_process += f"----- Judge -----\n{self.moderator_ans}\n"
            self.moderator_ans = eval(self.moderator_ans)
            self.config["Reason"] = self.moderator_ans["Reason"]
            self.config["debateAnswer"] = self.moderator_ans["Ultimate answer of the discussion topic"]
            self.print_answer()


if __name__ == "__main__":

    lines = list(questions_file.readlines())
    
    for line in tqdm.tqdm(lines):
        discussion_process = ""
        history = {}
        data = json.loads(line)
        debate_topic = data["text"]
        question_id = data["question_id"]
        image_path = data["image"]
        
        if image_path == 'COCO_val2014_000000231589.jpg' or image_path == 'COCO_val2014_000000275863.jpg' or image_path == 'COCO_val2014_000000163814.jpg' or image_path == 'COCO_val2014_000000355776.jpg':
            with open(out_file, "a") as f:
                f.write(json.dumps({
                    "question": debate_topic,
                    "answer": "error",
                    "question_id": question_id,
                    "image_path": data["image"],
                    "discussion_process": "None"
                }) + '\n')
            continue

        image_path = "..data/val2014/" + image_path

        config = json.load(open(f"./prompt_role.json", "r"))
        config['debate_topic'] = debate_topic

        debate = Debate(num_players=3, gemini_api_key=gemini_api_key, config=config, temperature=0, sleep_time=1,
                        img=image_path, discussion_process=discussion_process, history=history)
        debate.run()

        with open(out_file, "a") as f:
            f.write(json.dumps({
                "question": debate_topic,
                "answer": debate.config["debateAnswer"],
                "question_id": question_id,
                "image_path": data["image"],
                "discussion_process": debate.discussion_process
            }) + '\n')




