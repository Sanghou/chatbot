# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

from bothub_client.bot import BaseBot
from bothub_client.messages import Message
from .movies import BoxOffice
from .movies import LotteCinema

from .weather import get_weather


class Bot(BaseBot):
    """Represent a Bot logic which interacts with a user.

    BaseBot superclass have methods belows:

    * Send message
      * self.send_message(message, chat_id=None, channel=None)
    * Data Storage
      * self.set_project_data(data)
      * self.get_project_data()
      * self.set_user_data(data, user_id=None, channel=None)
      * self.get_user_data(user_id=None, channel=None)

    When you omit user_id and channel argument, it regarded as a user
    who triggered a bot.
    """

        

    def handle_message(self, event, context):
        """Handle a message received

        event is a dict and contains trigger info.

        {
           "trigger": "webhook",
           "channel": "<name>",
           "sender": {
              "id": "<chat_id>",
              "name": "<nickname>"
           },
           "content": "<message content>",
           "raw_data": <unmodified data itself webhook received>
        }
        """

        message = event.get('content')
        location = event.get('location')

        appid = '66ea1c7b7eca71a2e0ae3298ba932b2e'

        data = self.get_project_data()
        FLAG = data['FLAG']

        if location and FLAG == 1 :
            self.send_nearest_theaters(location['latitude'], location['longitude'],event)
            return

        if location and FLAG == 2 :
            self.send_weather(location['latitude'], location['longitude'],appid)
            return

        if not message:
            if event['new_joined']:
                self.send_chatroom_welcome_message(event)
            return

        if message == '영화순위':
            self.send_box_office(event)
        elif message == '근처 상영관 찾기':
            FLAG = 1
            data['FLAG'] = FLAG
            self.set_project_data(data)
            self.send_search_theater_message(event)
        elif message.startswith('/schedule'):
            _, theater_id, theater_name = message.split(maxsplit=2)
            self.send_theater_schedule(theater_id, theater_name, event)
        elif message == '메뉴보기':
            self.send_menu(event)
         # be aware of tailing space
        elif message.startswith('/show '):
            _, name = message.split()
            self.send_show(name, event)
         # be aware of tailing space
        elif message.startswith('/order_confirm '):
            _, name = message.split()
            self.send_order_confirm(name, event)
        elif message.startswith('/order '):
            _, name = message.split()
            self.send_order(name, event)
        elif message == 'help':
            self.send_welcome_message(event)
        elif message.startswith('/done'):
            self.send_drink_done(message, event)
        elif message == '/feedback':
            self.send_feedback_request()
        elif message == '날씨':
            FLAG = 2
            data['FLAG'] = FLAG
            self.set_project_data(data)
            msg = Message(event).set_text('날씨 확인을 위해 현재 위치를 전송해주세요.')\
                .add_location_request('Send Location')
            self.send_message(msg)
        elif message == '매드캠프':
            FLAG = 3
            data['FLAG'] = FLAG
            self.set_project_data(data)
            msg = Message(event).set_text('매드 캠프와 관련하여 무엇이든 물어보세요.')
            self.send_message(msg)

        elif '코딩' in message and '못' in message and FLAG ==3 :
            msg = Message(event).set_text('코딩을 못하더라도 잘 따라갈 수 있다고 83.3%의 학생들이 응답해주었습니다 :-) ' )
            self.send_message(msg)

        elif '만들' in message and FLAG == 3:
            msg = Message(event).set_text('많은 학생들이 안드로이드 APP 개발이나 게임 개발을 좋다고해요.')
            self.send_message(msg) 
        elif '배고프면' in message and FLAG == 3:
            msg = Message(event).set_text('매드캠프는 약 130만원 가량의 야식비를 지원해줘요!!')
            self.send_message(msg)
        
        elif '후회' in message and FLAG == 3:
            msg = Message(event).set_text('잠이 부족할 수 있고 따라가기 어려울 수 있지만 결코 후회하지는 않을거에요.')
            self.send_message(msg)

        elif '홍재민' in message and FLAG == 3:
            msg = Message(event).set_text('조교님은 매캠의 헬퍼로서 굳은 일을 도맡아 해주시는 천사님이에요. 많은 학생들이 사랑하고 있죠.')
            self.send_message(msg)

        elif '류석영' in message and FLAG == 3 :
            msg = Message(event).set_text('다섯 글자로 표현하자면, “행복전도사”, “카이의여신”, “항상열정적” 이라고 할 수 있겠네요. 전산의 인기녀로서 매우매우 많은 학생들에게 사랑과 존경을 한 몸에 받고 계십니다.')
            self.send_message(msg)

        elif '장병규' in message and FLAG == 3 :
            msg = Message(event).set_text('다섯 글자로 표현하자면, “동네아저씨”, “몰입전도사”, “야식후원자” 라고 할 수 있겠네요.')
            self.send_message(msg)

        else :
            data = self.get_user_data()
            wait_feedback = data.get('wait_feedback')
            if wait_feedback :
                self.send_feedback(message, event)
            else :
                self.send_message(" 명령을 이해하지 못했습니다 : {}".format(message))


    def send_welcome_message(self, event):
        message = Message(event).set_text('안녕하세요. 오늘을 함께할 cs496  채팅 봇입니다.\n ' +
        '시작가능하신 명령어로 \'영화순위\' ,  \'근처 상영관 찾기\' ,\'메뉴\', \'날씨\', \'매드캠프\'가 있습니다. ')\
        .add_quick_reply('영화순위')\
        .add_quick_reply('근처 상영관 찾기')\
        .add_quick_reply('메뉴보기')\
        .add_quick_reply('날씨')\
        .add_quick_reply('매드캠프')
        self.send_message(message)

    def send_weather(self, lat, lon, appid):
        weather = get_weather(lat,lon,appid)
        self.send_message(weather)


    def send_box_office(self, event):
        data = self.get_project_data()
        api_key = data.get('box_office_api_key')
        box_office = BoxOffice(api_key)
        movies = box_office.simplify(box_office.get_movies())
        rank_message = ', '.join(['{}. {}'.format(m['rank'], m['name']) for m in movies])
        response = '요즘 볼만한 영화들의 순위입니다\n{}'.format(rank_message)
        message = Message(event).set_text(response)\
                .add_quick_reply('영화순위')\
				.add_quick_reply('근처 상영관 찾기')
        self.send_message(message)

    def send_search_theater_message(self, event):
        message = Message(event).set_text('현재 계신 위치를 알려주세요')\
            .add_location_request('위치 전송하기')
        self.send_message(message)

    def send_nearest_theaters(self, latitude, longitude, event):
        cinema = LotteCinema()
        theaters = cinema.get_theater_list()
        nearest_theaters = cinema.filter_nearest_theater(theaters, latitude, longitude)
        
        message = Message(event).set_text('가장 가까운 상영관들입니다. \n' +  '상영 시간표를 확인하세요:')
        for theater in nearest_theaters:
            data = '/schedule {} {}'.format(theater['TheaterID'], theater['TheaterName'])
            message.add_postback_button(theater['TheaterName'], data)

        message.add_quick_reply("영화순위")
        self.send_message(message)

    def send_theater_schedule(self, theater_id, theater_name, event):
        c = LotteCinema()
        movie_id_to_info = c.get_movie_list(theater_id)
        text = '{}의 상영시간표입니다.\n\n'.format(theater_name)

        movie_schedules = []
        for info in movie_id_to_info.values():
            movie_schedules.append('* {}\n  {}'.format(info['Name'], ' '.join([schedule['StartTime'] for schedule in info['Schedules']])))

        message = Message(event).set_text(text + '\n'.join(movie_schedules))\
            .add_quick_reply('영화순위')\
            .add_quick_reply('근처 상영관 찾기')
        self.send_message(message)


# menu order


    def send_chatroom_welcome_message(self, event):
        self.remember_chatroom(event)
        message = Message(event).set_text('안녕하세요? 봇입니다.\n'\
                                                  '필요한 명령어는 help를 입력해보세요.')
        self.send_message(message)

    def remember_chatroom(self,event):
        chat_id = event.get('chat_id')
        data = self.get_project_data()
        data['chat_id'] = chat_id
        self.set_project_data(data)


    def send_menu(self, event):
        menu = self.get_project_data()['menu']
        names = [name for name in menu.keys()]
        
        message = Message(event).set_text('어떤 음료를 원하시나요?')
        for name in names:
            message.add_postback_button(name,'/show {}'.format(name))
        self.send_message(message)
         
    def send_show(self, name, event):
        menu = self.get_project_data()['menu']
        selected_menu = menu[name]
        text = '{name}는 {description}\n가격은 {price}원이예요.'.format(name=name, **selected_menu)
        message = Message(event).set_text(text)\
            .add_postback_button('{} 주문'.format(name), payload = '/order {}'.format(name))\
            .add_postback_button('메뉴보기', '메뉴보기')
        self.send_message(message)

    def send_order_confirm(self, name, event):
        message = Message(event).set_text('{}를 주문하시겠어요?'.format(name))\
            .add_postback_button('예', '/order {}'.format(name))\
            .add_postback_button('취소', '메뉴보기')
        self.send_message(message)

    def send_order(self,name, event, quantity = 1):
        self.send_message('{}를 {}잔 주문했습니다. 음료가 준비되면 알려드릴께요.'.format(name, quantity))
        chat_id = self.get_project_data().get('chat_id')
        order_message = Message(event).set_text('{} {}잔 주문 들어왔습니다!'.format(name, quantity))\
            .add_postback_button('완료', '/done {} {}'.format(event['sender']['id'], name))
        self.send_message(order_message, chat_id=chat_id)

    def send_drink_done(self, content, event):
        _, sender_id, menu_name = content.split()
        self.send_message('{}가 준비되었습니다. 카운터에서 수령해주세요.'.format(menu_name), chat_id=sender_id)
        message = Message(event).set_text('저희 가게를 이용하신 경험을 말씀해주시면 많은 도움이 됩니다.')\
            .add_postback_button('평가하기', '/feedback')
        self.send_message(message, chat_id=sender_id)
        self.send_message('고객분께 음료 완료 알림을 전송했습니다.')

    def send_feedback_request(self):
        self.send_message('음료는 맛있게 즐기셨나요? 어떤 경험을 하셨는지 알려주세요. 격려, 꾸지람 모두 큰 도움이 됩니다.')
        data = self.get_user_data()
        data['wait_feedback'] = True
        self.set_user_data(data)

    def send_feedback(self, content, event):
        chat_id = self.get_project_data().get('chat_id')
        self.send_message('고객의 평가 메세지입니다:\n{}'.format(content), chat_id=chat_id)
       
        message = Message(event).set_text('평가해주셔서 감사합니다!')\
            .add_quick_reply('메뉴보기')
        self.send_message(message)
     
        data = self.get_user_data()
        data['wait_feedback'] = False
        self.set_user_data(data)
