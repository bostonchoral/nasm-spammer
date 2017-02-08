require 'mechanize'
require 'highline/import'
require 'csv'

class NasmParser < Mechanize
  HOME = 'http://nasm.arts-accredit.org/'
  SCHOOL = 'div.wpb_wrapper h2'
  SITE = 'div.wpb_wrapper h2 + p > a'

  def scan_contacts(page, prefix='')
    info = page.search("h3:contains('Contacts')#{prefix} + p").inner_html
    if info.empty?
      []
    else
      name, title, department = info.split('<br>')[0].split(',').map{|s| s.strip.squeeze}
      email = info[/E-Mail: <[^>]+>([^<]+)<\/a>/, 1]
      [[name, email, title, department]] + scan_contacts(page, "#{prefix} + p")
    end
  end

  def process(user, password)
    user_agent_alias = 'Mac Safari'
    get HOME

    # login
    click page.link_with(:text => /login/i)
    page.form_with(:class => /login/i) do |f|
      f.username = user
      f.password = password
      f.click_button
    end

    # list members
    click page.link_with(:text => /advanced search/i)
    page.form_with(:id => 'institution-search').click_button

    # fetch and process one member
    l = page.links_with(:href => /\?id=/i)

    l.each do |link|
      transact do
        click link
        school = page.search(SCHOOL).inner_html
        site = page.search(SITE).inner_html
        contacts = scan_contacts(page)
        if contacts.empty?
          yield [school, site, '', '', '', '', '']
        else
          contacts.each do |contact|
            yield [school, site] + contact
          end
        end
      end
    end

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
