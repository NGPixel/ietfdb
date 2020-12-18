# Generated by Django 2.2.17 on 2020-12-18 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0038_auto_20201109_0439'),
    ]

    operations = [
        migrations.DeleteModel(
            name='HistoricalGroupFeatures',
        ),
    ]

# In case these are ever needed again, here's what had been captured.
# Note that many of the values are not well formed as JSONFields and need to be manually corrected if they are brought back.
# 
# -- Table structure for table `group_historicalgroupfeatures`
# DROP TABLE IF EXISTS `group_historicalgroupfeatures`;
# CREATE TABLE `group_historicalgroupfeatures` (
#   KEY `group_historicalgroupfeatures_agenda_type_id_089e752b` (`agenda_type_id`),
#   KEY `group_historicalgroupfeatures_history_user_id_0d1368d2` (`history_user_id`),
#   KEY `group_historicalgroupfeatures_type_id_4ed21f10` (`type_id`)
# -- Dumping data for table `group_historicalgroupfeatures`
# LOCK TABLES `group_historicalgroupfeatures` WRITE;
# /*!40000 ALTER TABLE `group_historicalgroupfeatures` DISABLE KEYS */;
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,0,0,1,0,0,0,'ietf.group.views.group_about','ietf.group.views.group_about','slides','chair,lead',1,NULL,'2018-07-15 08:23:57.183851','~','ietf',433,'ietf',0,0,0,0,0,'chair,secr,member',0,0,'ad,chair,delegate,secr','[\"ad\",\"chair\",\"delegate\",\"secr\"]','[\"ad\",\"chair\"]','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,0,0,0,0,0,0,'ietf.group.views.group_about','ietf.group.views.group_about','slides','ad',2,NULL,'2018-07-19 13:07:33.440449','~','ietf',433,'area',0,0,0,0,0,'chair,secr,member',0,0,'ad,chair,delegate,secr','[\"ad\",\"chair\",\"delegate\",\"secr\"]','[\"ad\",\"chair\"]','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,1,0,1,0,0,0,'ietf.group.views.group_about','ietf.group.views.group_about','[\"slides\"]','[\"chair\"]',3,NULL,'2019-02-04 07:41:05.566267','~','ietf',433,'ag',1,1,1,1,1,'[\"chair\",\"secr\"]',1,1,'[\"ad\",\"chair\",\"delegate\",\"secr\"]','[\"chair\",\"delegate\",\"secr\"]','[\"ad\",\"chair\",\"delegate\"]','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,0,0,1,0,1,0,'ietf.group.views.group_about','ietf.group.views.group_about','\"[\\\"slides\\\"]\"','\"[\\\"chair\\\"]\"',4,NULL,'2019-03-07 14:32:17.595737','~','ietf',433,'adhoc',0,1,0,1,1,'\"[\\\"chair\\\",\\\"delegate\\\",\\\"matman\\\"]\"',1,1,'\"[\\\"chair\\\",\\\"delegate\\\",\\\"matman\\\"]\"','\"[\\\"chair\\\"]\"','\"[\\\"chair\\\",\\\"delegate\\\"]\"','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,0,0,1,0,1,0,'ietf.group.views.group_about','ietf.group.views.group_about','\"[\\\"slides\\\"]\"','\"[\\\"chair\\\"]\"',5,NULL,'2019-03-07 15:13:37.631043','~','ietf',433,'adhoc',0,1,0,1,1,'\"[\\\"chair\\\",\\\"lead\\\",\\\"delegate\\\",\\\"matman\\\"]\"',1,1,'\"[\\\"chair\\\",\\\"lead\\\",\\\"delegate\\\",\\\"matman\\\"]\"','\"[\\\"chair\\\"]\"','\"[\\\"chair\\\",\\\"lead\\\",\\\"delegate\\\"]\"','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,0,1,1,0,0,0,'ietf.group.views.group_about','ietf.group.views.group_about','[\"slides\"]','[\"chair\"]',6,NULL,'2019-03-13 11:02:32.696034','~','ietf',433,'team',0,1,1,0,0,'[\"chair\",\"member\",\"matman\"]',0,0,'[\"chair\",\"matman\"]','[\"chair\"]','[\"chair\"]','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,0,1,1,0,0,0,'ietf.group.views.group_about','ietf.group.views.group_about','[\"slides\"]','[\"chair\"]',7,NULL,'2019-03-13 13:59:38.964013','~','ietf',433,'team',0,1,1,0,0,'[\"chair\",\"member\",\"matman\"]',0,0,'[\"chair\",\"matman\"]','[\"chair\"]','[\"chair\"]','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,0,0,1,0,1,0,'ietf.group.views.group_about','ietf.group.views.group_about','[\"slides\"]','[\"chair\"]',8,NULL,'2019-03-13 14:02:03.061530','~','ietf',433,'adhoc',0,1,0,1,1,'[\"chair\",\"lead\",\"delegate\",\"matman\"]',1,1,'[\"chair\",\"lead\",\"delegate\",\"matman\"]','[\"chair\"]','[\"chair\",\"lead\",\"delegate\"]','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,0,0,0,0,0,0,'ietf.group.views.group_about','ietf.group.views.group_about','\"[]\"','[\"chair\"]',9,NULL,'2019-03-13 14:04:12.810180','~','ad',433,'iesg',0,0,1,0,0,'[\"chair\",\"delegate\",\"member\"]',0,1,'[\"chair\",\"delegate\",\"member\"]','[\"chair\"]','[\"chair\",\"delegate\"]','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,0,0,0,0,0,0,'ietf.group.views.group_about','ietf.group.views.group_about','[\"slides\"]','[\"chair\",\"lead\"]',10,NULL,'2019-03-13 14:05:47.617726','~','ad',433,'ise',0,0,1,0,0,'[\"chair\",\"delegate\"]',0,1,'[\"chair\",\"delegate\"]','[\"chair\"]','[\"chair\",\"delegate\"]','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (1,1,1,0,1,0,1,1,'ietf.group.views.group_about','ietf.group.views.group_documents','[\"slides\"]','[\"chair\"]',11,NULL,'2019-04-23 04:11:30.770056','~','ietf',433,'rg',1,1,0,1,1,'[\"chair\",\"delegate\",\"secr\"]',1,1,'[\"chair\",\"delegate\",\"secr\"]','[\"chair\",\"delegate\",\"secr\"]','[\"chair\",\"delegate\"]','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (1,0,1,0,0,0,0,0,'ietf.group.views.group_about','ietf.group.views.group_about','[\"slides\"]','[\"lead\"]',12,NULL,'2019-04-24 04:03:41.967314','~','ad',433,'program',0,0,1,0,0,'[\"lead\",\"secr\"]',0,0,'[\"lead\",\"secr\"]','[\"lead\",\"secr\"]','[\"lead\",\"secr\"]','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,0,0,0,0,0,0,'ietf.group.views.group_about','ietf.group.views.group_about','[\"slides\"]','[\"chair\",\"advisor\"]',13,NULL,'2019-04-29 04:44:26.522936','~','side',433,'nomcom',0,1,1,0,0,'[\"chair\",\"member\",\"advisor\"]',0,1,'[\"chair\"]','[\"chair\"]','[\"chair\",\"advisor\"]','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,0,0,0,0,0,0,'ietf.group.views.group_about','ietf.group.views.group_about','[\"slides\"]','[\"chair\"]',14,NULL,'2019-06-26 13:28:11.695889','+','ietf',433,'admin',0,0,0,0,0,'[\"chair\"]',0,0,'[\"chair\"]','[\"chair\"]','[\"chair\"]','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,0,0,0,0,0,0,'ietf.group.views.group_about','ietf.group.views.group_about','[\"slides\"]','[\"chair\"]',15,NULL,'2019-06-26 13:29:29.706999','+','ietf',433,'iana',0,0,0,0,0,'[\"chair\"]',0,0,'[\"chair\"]','[\"chair\"]','[\"chair\"]','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,1,0,0,0,0,0,'ietf.group.views.group_about','ietf.group.views.group_about','[\"slides\"]','[\"chair\",\"lead\"]',16,NULL,'2019-07-17 04:20:03.049554','~','ad',433,'ise',0,0,1,0,0,'[\"chair\",\"delegate\"]',0,1,'[\"chair\",\"delegate\"]','[\"chair\"]','[\"chair\",\"delegate\"]','[\"Secretariat\"]','[]');
# INSERT INTO `group_historicalgroupfeatures` (`has_milestones`, `has_chartering_process`, `has_documents`, `has_nonsession_materials`, `has_meetings`, `has_reviews`, `has_default_jabber`, `customize_workflow`, `about_page`, `default_tab`, `material_types`, `admin_roles`, `history_id`, `history_change_reason`, `history_date`, `history_type`, `agenda_type_id`, `history_user_id`, `type_id`, `acts_like_wg`, `create_wiki`, `custom_group_roles`, `has_session_materials`, `is_schedulable`, `role_order`, `show_on_agenda`, `req_subm_approval`, `matman_roles`, `docman_roles`, `groupman_roles`, `groupman_authroles`, `default_used_roles`) VALUES (0,0,0,0,1,1,0,0,'ietf.group.views.group_about','ietf.group.views.review_requests','[\n    \"slides\"\n]','[\n    \"chair\",\n    \"secr\"\n]',17,NULL,'2020-11-23 10:19:39.119039','~','ietf',420,'review',0,1,1,0,0,'[\n    \"chair\",\n    \"secr\"\n]',0,1,'[\n    \"ad\",\n    \"secr\"\n]','[\n    \"secr\"\n]','[\n    \"ad\",\n    \"secr\"\n]','[\n    \"Secretariat\"\n]','[\n    \"ad\",\n    \"chair\",\n    \"reviewer\",\n    \"secr\"\n]');
# /*!40000 ALTER TABLE `group_historicalgroupfeatures` ENABLE KEYS */;
# 