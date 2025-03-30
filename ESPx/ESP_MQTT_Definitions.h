#ifndef ESP_MQTT
#define ESP_MQTT
// Küche
#define topic_status_kueche_motion ("home/kueche/motion/state")
#define topic_status_kueche_temperatur ("home/kueche/temperatur/state")
#define topic_status_kueche_helligkeit ("home/kueche/helligkeit/state")
#define topic_set_kueche_alarmanlage ("home/kueche/alarmanlage/set")

// Wohnzimmer
#define topic_status_wohnzimmer_motion ("home/wohnzimmer/motion/state")
#define topic_status_wohnzimmer_temperatur ("home/wohnzimmer/temperatur/state")
#define topic_status_wohnzimmer_helligkeit ("home/wohnzimmer/helligkeit/state")
#define topic_set_wohnzimmer_alarmanlage ("home/wohnzimmer/alarmanlage/set")
#define topic_set_wohnzimmer_buzzer ("home/wohnzimmer/buzzer/set")

// Flur
#define topic_status_flur_motion ("home/flur/motion/state")
#define topic_status_flur_will ("clientstatus/RFIDReader")
#define topic_set_flur_rfidreader ("/home/flur/rfidreader/set")

// Garage, Garagentor
#define topic_status_garagentor_will ("clientstatus/Garagentor")
#define topic_set_garagentor_trigger ("home/garage/tor/set")
#define topic_status_garagentor_status ("home/garage/tor/state") // offen, geschlossen per Magnetkontakt o.ä.
#define topic_status_garage_motion ("home/garage/motion/state")
#define topic_status_garage_temperatur ("home/garage/temperatur/state")


// Generisch
#define client_online_message ("ONLINE")
#define client_offline_message ("OFFLINE")

// Alte Definitionen
#define topic_status_wohnzimmer_motion_old ("alarm/wohnzimmer/detected")
#define topic_status_auto_motion_old ("alarm/auto/detected")
#define topic_set_kueche_alarmanlage_old ("alarm/auto/motion")
#define topic_set_wohnzimmer_alarmanlage_old ("alarm/wohnzimmer/motion")
#define topic_set_wohnzimmer_buzzer_old ("buzzer/wohnzimmer")
#define topic_set_flur_rfidreader_old ("rfid_reader/uid")

#endif
