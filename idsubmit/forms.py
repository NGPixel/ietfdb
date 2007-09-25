# Copyright The IETF Trust 2007, All Rights Reserved

from django import newforms as forms

class IDUploadForm(forms.Form):
    txt_file = forms.Field(widget=forms.FileInput(), label='.txt format *')
    xml_file = forms.Field(widget=forms.FileInput(), required=False, label='.xml format')
    pdf_file = forms.Field(widget=forms.FileInput(), required=False, label='.pdf format')
    ps_file = forms.Field(widget=forms.FileInput(), required=False, label='.ps format')
    
    def file_content(self):
        txt_file = self.clean_data['txt_file']
        return txt_file

    def save(self,filename,revision):
        file_content = self.clean_data['txt_file']['content']
        output_id = open('/Library/WebServer/Documents/tempids/'+filename+'-'+revision+'.txt','w')
        output_id.write(file_content)
        output_id.close()
        for extra_type in [{'file_type':'xml_file','file_ext':'.xml'}, {'file_type':'pdf_file','file_ext':'.pdf'},{'file_type':'ps_file','file_ext':'.ps'}]:
            file_type=extra_type['file_type']
            file_ext=extra_type['file_ext']
            if self.clean_data[file_type]:
                extra_file_content = self.clean_data[file_type]['content']
                extra_output_id = open('/home/mlee/tempids/'+filename+'-'+revision+file_ext,'w')
                extra_output_id.write(extra_file_content)
                extra_output_id.close()
        return 1

