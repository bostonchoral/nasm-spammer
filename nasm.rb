require 'mechanize'
require 'highline/import'
require 'csv'

class NasmParser < Mechanize
  HOME = 'http://nasm.arts-accredit.org/'
  SCHOOL = /<h2>(.*)<\/h2>/
  SITE = /Web Site: .*">(.*)<\/a>/
  CONTACT = /<br>([^<]]*) ([^<]]*), <i>(.*)<\/i>.*E-Mail *([^<]]*) *<br>/

  def process(user, password)
    user_agent_alias = 'Mac Safari'
    get HOME

    # login
    click page.link_with(:text => /login/i)
    page.form_with(:action => /login/i) do |f|
      f.login = user
      f.password = password
      f.click_button
    end

    # list members
    click page.link_with(:text => /directory/i)
    click page.link_with(:text => 'ACCREDITED INSTITUTIONAL MEMBERS')
    page.form_with(:action => /List_Accredited_Members/).click_button

    # fetch and process one member
    l = page.links_with(:href => /memberid/i)
    l.each do |link|
      transact do
        click link
        data = page.search('td.maintxt td.maintxt').inner_html
        school = data.scan(SCHOOL).flatten.first
        site = data.scan(SITE).flatten.first
        contacts = data.scan(CONTACT)
        if contacts.empty?
          yield [school, site, '', '', '', '']
        else
          contacts.each do |contact|
            yield [school, site] + contact
          end
        end
      end
    end

    click page.link_with(:text => /logout/i)
    l.length
  end
end

say("This script will attempt to log in to the NASM member directory and produce
a CSV file containing contact information for all members. You can then import
this CSV into Excel, Google Drive, etc.\n\n")
u = ask('username: ')
p = ask('password: ') { |q| q.echo = '*' }
say("Processing, this may take a while...")

n = CSV.open('nasm.csv', 'w') do |csv|
  NasmParser.new.process(u,p) do |row|
    csv << row
    say("\r<%= HighLine.Style(:erase_line).code %> #{row[0]} ")
  end
end

say("\nProcessed #{n} records. Data has been saved in nasm.csv")
