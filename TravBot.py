# -*- coding: utf-8 -*-
import json
import random
import re
import time
from collections import OrderedDict
from collections import defaultdict

from bs4 import BeautifulSoup
from selenium import webdriver


def random_sleep():
    time.sleep(random.randint(3, 13))


ins = json.load(open("upgrades1.json", encoding="utf8"), object_pairs_hook=OrderedDict)

base_url = ins["login"]["server_url"]
land_url = base_url + "dorf1.php"
city_url = base_url + "dorf2.php"
username = ins["login"]["username"]
password = ins["login"]["password"]
browser = webdriver.Edge()

browser.get(land_url)
random_sleep()


def login():
    login_url = base_url + "login.php"
    browser.get(login_url)
    username_input = browser.find_element_by_name("name")
    password_input = browser.find_element_by_name("password")
    # if str(username_input.get_property("text")) == "":
    username_input.send_keys(username)
    # if str(password_input.get_property("text")) == "":
    password_input.send_keys(password)
    browser.find_element_by_id("s1").click()
    random_sleep()


def sleep_for_building_duration():
    random_sleep()
    if len(browser.find_elements_by_class_name("buildDuration")) < 1:
        return
    build_duration = int(
        browser.find_element_by_class_name("buildDuration").find_element_by_tag_name("span").get_attribute(
            "value"))
    if build_duration > 1:
        print("something is building, sleeping for " + str(build_duration) + " seconds")
        time.sleep(build_duration + 10)
        random_sleep()
        browser.refresh()


if len(browser.find_elements_by_class_name("login")) > 0:
    login()

sleep_for_building_duration()

city_building_areas = {}


def update_city_areas():
    global city_building_areas
    if browser.current_url is not city_url:
        browser.get(city_url)
        random_sleep()
    city_building_areas = defaultdict(list)
    for i in browser.find_elements_by_tag_name("area"):
        if str(i.get_attribute('href')) == 'build.php?id=40':
            continue  # This is the wall, the wall has to die, we don't want the wall, the wall is ugly and impractical.
        soup = BeautifulSoup(i.get_property("alt"), 'html.parser')
        try:
            level = int(re.search("\d+", str(soup.find("span", attrs={'class': 'level'}))).group(0))
        except AttributeError:
            level = 0
        area = {'level': level, 'href': i.get_attribute('href')}
        city_building_areas[str(i.get_property("alt")).split(" <")[0]].append(area)
    city_building_areas = dict(city_building_areas)
    for i in city_building_areas.keys():
        city_building_areas[i] = sorted(city_building_areas[i], key=lambda k: k['level'])
    print("updated city areas: " + str(city_building_areas))


def upgrade_area_until_level(instructions, name):
    update_city_areas()
    random_sleep()
    while instructions[name] - 1 > city_building_areas[name][0]['level']:
        update_city_areas()
        random_sleep()
        browser.get(city_building_areas[name][0]['href'])
        random_sleep()
        try:
            browser.find_element_by_class_name("green build").click()
        except:
            time_til_enough_resources = int(
                browser.find_element_by_class_name("statusMessage").find_element_by_class_name("timer").get_attribute(
                    "value"))
            print("not enough resources to buy, waiting " + str(time_til_enough_resources) + " to buy")
            time.sleep(time_til_enough_resources)
            random_sleep()
            upgrade_area_until_level(instructions, name)
            return
        random_sleep()
        browser.get(city_url)
        random_sleep()
        sleep_for_building_duration()


def build_new_building_city(name):
    update_city_areas()
    random_sleep()
    browser.get(city_building_areas['Byggeplads'][0]['href'])
    random_sleep()
    for k in browser.find_elements_by_class_name("buildingWrapper"):
        if str(k.find_element_by_tag_name("h2").text) == name:
            try:
                k.find_element_by_class_name("green new").click()
            except:
                time_til_enough_resources = int(
                    k.find_element_by_class_name("statusMessage").find_element_by_class_name(
                        "timer").get_attribute(
                        "value"))
                print("not enough resources to buy, waiting " + str(time_til_enough_resources) + " to buy")
                time.sleep(time_til_enough_resources)
                random_sleep()
                build_new_building_city(name)
                return
            random_sleep()
            sleep_for_building_duration()
            return


def handle_city(instructions):
    browser.get(city_url)
    random_sleep()
    update_city_areas()
    random_sleep()
    instructions = dict(instructions)
    for key in instructions.keys():
        random_sleep()
        print("key: " + key + " value " + str(instructions[key]))
        if key not in city_building_areas.keys():
            build_new_building_city(key)
            random_sleep()
        upgrade_area_until_level(instructions, key)


resources = dict()


def update_resources():
    global resources
    free_crops = int(
        re.search('\d+', str(browser.find_element_by_id("stockBarFreeCrop").text).replace(".", "")).group(0))
    lumber = int(str(browser.find_element_by_id("l1").text).replace(".", ""))
    clay = int(str(browser.find_element_by_id("l2").text).replace(".", ""))
    iron = int(str(browser.find_element_by_id("l3").text).replace(".", ""))
    crops = int(str(browser.find_element_by_id("l4").text).replace(".", ""))
    res = {'freeCrops': free_crops,
           'resources': [{'type': 'Skovhugger', 'amount': lumber}, {'type': 'Lergrav', 'amount': clay},
                         {'type': 'Jernmine', 'amount': iron}, {'type': 'Kornavler', 'amount': crops}]}
    res['resources'] = sorted(res['resources'], key=lambda k: k['amount'])
    print("resources: " + str(res))
    resources = res


land_areas = defaultdict(list)


def update_land_areas():
    global land_areas
    if browser.current_url is not land_url:
        browser.get(land_url)
        random_sleep()
    land_areas = defaultdict(list)
    for i in browser.find_elements_by_tag_name('area'):
        if str(i.get_attribute('alt')) == 'Bygninger':
            continue
        area = {'level': int(str(i.get_attribute('alt')).split(' ')[-1]), 'href': i.get_attribute('href')}
        land_areas[str(i.get_attribute('alt')).split(' ')[0]].append(area)
    land_areas = dict(land_areas)
    for i in land_areas.keys():
        land_areas[i] = sorted(land_areas[i], key=lambda k: k['level'])
    print("updated land areas: " + str(land_areas))


def done_with_upgrading_land(instructions):
    update_land_areas()
    random_sleep()
    done = []
    for k in instructions.keys():
        done.append(land_areas[k][0]['level'] >= instructions[k])
    return all(done)


def what_to_upgrade(instructions):
    update_resources()
    random_sleep()
    update_land_areas()
    random_sleep()
    if resources['freeCrops'] <= 5:
        return "Kornavler"
    else:
        for r in range(0, len(resources['resources'])):
            k = resources['resources'][r]['type']
            random_sleep()
            if land_areas[k][0]['level'] < instructions[k]:
                return k


def upgrade_land(instructions):
    random_sleep()
    ug = what_to_upgrade(instructions)
    random_sleep()
    print("upgrading " + ug)
    browser.get(land_areas[ug][0]['href'])
    browser.refresh()
    random_sleep()
    try:
        browser.find_element_by_class_name("green build").click()
    except:
        time_til_enough_resources = int(
            browser.find_element_by_class_name("statusMessage").find_element_by_class_name("timer").get_attribute(
                "value"))
        print("not enough resources to buy, waiting " + str(time_til_enough_resources) + " to buy")
        time.sleep(time_til_enough_resources)
        random_sleep()
        upgrade_land(instructions)
        return
    random_sleep()
    sleep_for_building_duration()


def handle_land(instructions):
    browser.get(land_url)
    random_sleep()
    update_land_areas()
    random_sleep()
    while not done_with_upgrading_land(instructions):
        upgrade_land(instructions)


def change_to_village(village_name):
    print("changing to Village:" + str(village_name))


for instruction in ins['instructions']:
    change_to_village(instruction['village'])
    random_sleep()
    if instruction['location'] == "city":
        handle_city(instruction['instructions'])
    else:
        handle_land(instruction['instructions'])
