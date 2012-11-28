#!/usr/bin/python
import sys
import re

def main(filename):
    f = open(filename)
    lines = f.readlines()
    f.close()
    joined = '\n'.join(lines)

    re_school = re.compile(r'<h2>(.*)</h2>')
    re_site = re.compile(r'Web Site: .*">(.*)</a>')
    re_names = re.compile(r'<br>(.*) (.*), <i>(.*)</i>')
    re_email = re.compile(r'E-Mail *(.*)<br>')

    g_school = re_school.findall(joined)
    if (len(g_school) < 1):
        warn('no school found for file %s' % filename)
    else:
        school = g_school[0]
    
    g_site = re_site.findall(joined)
    if (len(g_site) < 1):
        warn('no website found for file %s' % filename)
    else:
        site = g_site[0]

    g_names = re_names.findall(joined)
    if (len(g_names) < 1):
        warn('no names found for file %s' % filename)
    else:
        fnames = [f for (f,l,t) in g_names]
        lnames = [l for (f,l,t) in g_names]
        titles = [t for (f,l,t) in g_names]

    emails = None
    g_email = re_email.findall(joined)
    if (len(g_email) < 1):
        warn('no emails found for file %s' % filename)
    else:
        emails = g_email

    pattern = '"%s","%s","%s","%s","%s","%s"'

    if (emails):
        for i in range(len(emails)):
            print pattern % (school, fnames[i], lnames[i], titles[i], emails[i], site)
    else:
        print pattern % (school, '','','','',site)

def warn(message):
    return
    #print 'WARN:', message

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage:', sys.argv[0], '<files>'
    else:
        for f in sys.argv[1:]:
            main(f)
