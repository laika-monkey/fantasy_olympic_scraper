#!/usr/bin/perl

use strict;
use File::Slurp;
use File::Compare;
use File::Copy;

#_get medal data
my $SRC_URL = 'https://en.as.com/resultados/juegos_olimpicos/medallero/';
my $PAGE;
while (1) {
    print "Downloading medal count...\n";
    system "wget $SRC_URL";
    system 'cat index.html | tr -d "\t\n\r" > index.html.out';
    $PAGE = read_file('index.html.out');
    last if -e 'index.html'; }
unlink('index.html', 'index.html.out');

#_scrape country names and counts
my $REGEX='<span class="team-inline">(.+?)</span></a></td>' .
	'<td><span class="d-m">(\d+)</span></td>' .
	'<td><span class="d-m">(\d+)</span></td>' .
	'<td><span class="d-m">(\d+)</span></td>';

#_print output to csv
print "Scraping medal count from page...\n";
my $NEW = 'standings.latest.txt';
my $OLD = 'standings.txt';
open(F, '>', $NEW) or die $!;
while ($PAGE =~ /$REGEX/g) {
	print F "$1,$2,$3,$4\n";}
close(F);

#_if they've changed, launch discord spammer
# Main problem is that this updates if ANY country gets a medal, not just
# germane ones
if (compare($NEW, $OLD) != 0) {
	print "Launching updated scores...\n";
    copy $NEW, $OLD;
    system "./score_calc.py";	
	};

