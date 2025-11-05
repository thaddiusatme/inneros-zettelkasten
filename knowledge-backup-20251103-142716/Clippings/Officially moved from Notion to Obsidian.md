---
title: "Officially moved from Notion to Obsidian"
source: "https://www.reddit.com/r/ObsidianMD/comments/1o3xo6g/officially_moved_from_notion_to_obsidian/"
author:
  - "[[chinychon]]"
published: 2025-10-11
created: 2025-10-14
description:
tags:
  - "clippings"
---
I was so tired of Notion shoving AI into everything, and I literally created a telegram bot for quick capture because loading up the (Notion) app on my phone was so slow. Now I just swipe up to toggle TaskNotes: create new task.

I am loving the set up. The community is awesome. I can combine my handwritten notes with my typed notes all in one place with Excalidraw. And hotkeys! And pomodoro! And themes! And I can edit files via NeoVim! (Came from using the zk NeoVim plugin).

I hope the app stays this way forever to be honest. Couldn't bear to see it become bloated (though welcoming the bases updates).

---

## Comments

> **algeraa** • [99 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niy6itw/) •
> 
> I'm new to obsidian. This setup is great. How would I replicate it? Thank you
> 
> > **chinychon** • [104 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niybvta/) •
> > 
> > I'm not sure if this guide is very beginner friendly, though I'm a beginner too. It's gonna be a long one.
> > 
> > **Main plugins:**
> > 
> > 1. Homepage -> I have it toggle reading mode on opening (under 'commands')
> > 2. Columns
> > 3. Excalidraw -> customize your folders under the 'saving' section
> > 4. TaskNotes -> i changed the status names to 'none', 'seed', 'growing', 'ripe'
> > 
> > Theme: Obsidian Gruvbox  
> > Useful Custom Hotkeys:
> > 
> > Ctrl + Space => Find file
> > Ctrl + Shift + Space => Command Palette
> > Alt + Space => TaskNotes: Create new task (Swipe up on mobile via toolbar settings)
> > Alt + R => Toggle reading mode
> > 
> > **Set up:**
> > 
> > **Capture**  
> > simple embedded capture.base file (filters via in folder 'capture')  
> > I also add these to my project notes (new base with the same filter, additional filter of being linked to my project \[TaskNotes does this for you\])
> > 
> > **The Vault**  
> > Links to bases or excalidraw files that I frequent.  
> > I use excalidraw templates for my habit tracker.
> > 
> > > **chinychon** • [32 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niybydl/) •
> > > 
> > > **Journal**  
> > > Embedded base, filtered by folder
> > > 
> > > **Projects**  
> > > Embedded base, filtered by tag and status (I only show 'seed' and 'growing')
> > > 
> > > **Calendar:**  
> > > using the TaskNotes bases view  
> > > filter:
> > > 
> > > file.inFolder("Home/AllTasks")
> > > file.hasTag("meeting")
> > > scheduled >= today()
> > > scheduled <= today() + "7 days"
> > > 
> > > **Daily:**  
> > > using the TaskNotes bases view  
> > > filter:
> > > 
> > > file.inFolder("Home/AllTasks")
> > > !file.hasTag("meeting")
> > > scheduled == today()
> > > 
> > > I also have two secondary views that show the day before and the day after (comes in handy)
> > > 
> > > **Weekly:**  
> > > using the TaskNotes bases view  
> > > filter:
> > > 
> > > file.inFolder("Home/AllTasks")
> > > !file.hasTag("meeting")
> > > !status.contains("ripe")
> > > scheduled >= today()
> > > scheduled <= today() + "7 days"
> > > 
> > > **Resonance Calendar:**  
> > > Embedded base, filtered by 'surface' tag and 'resonance' property. Basically surfaces notes that I want to be able to access easily.
> > > 
> > > **Personal:**  
> > > A bunch of embedded bases, just limited to 5 results each.
> > > 
> > > **EverNevermor** • [4 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niz9h0t/) •
> > > 
> > > I'd love to know your "capture" process (and I love the idea of quickly capturing directly into a base that can then be displayed; it's wonderful). I find the quick capture is my current bottleneck (i'm on Apple ecosystem, have tried shortcuts directly to my daily note, using Drafts app connection to Obsidian etc... and currently have a shortcut to a daily Apple note that I then manually add or process in my daily note in Obsidian or whatever note i need to make from it)
> 
> **chichris** • [8 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niybggh/) •
> 
> It does look slick as hell. One of the best ones I’ve seen so far.
> 
> **Saasoso** • [5 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niy8koo/) •
> 
> tasknotes and personalize the gui yourself
> 
> **oas1893** • [6 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niy7zur/) •
> 
> +1
> 
> > **didnt\_want\_to\_simp** • [4 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niy8gru/) •
> > 
> > +1

> **Aware-Glass-8030** • [34 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niyb6tm/) •
> 
> Notion's AI is a catastrophe anyway. It's by FAR the worst I've seen in any agentic AI implementation.
> 
> There's literally no redeeming qualities about Notion. It's slow, it can't take more than a couple thousand words pasted into a note without saying "this is too much text for me try importing the note instead" (like seriously?!? it's a note taking app... LOL), AND you have to manually switch on "save offline" on individual notes so you can save your notes offline?
> 
> Not to mention it's super slow and often unresponsive.
> 
> Who even uses this crap?
> 
> I went from Obsidian to Notion for a brief few days and did a rapid 180 back to Obsidian.
> 
> What. A. Nightmare.
> 
> > **Junior\_B** • [11 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/nizci7y/) •
> > 
> > Easy database tables brought me to Notion did a year and a half sentence; the second bases came out I got paroled.

> **Failed\_Alarm** • [13 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niy6a59/) •
> 
> Welcome to the club! 

> **404MoralsNotFound** • [12 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/nj1o6qm/) •
> 
> Your organizing skills are incredible. My ADHD brain could never-ever. Even after using obsidian for 2 years 🤣 Lowkey jealous and made me cleanup my vault for a few mins.

> **fsmontenegro** • [8 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niy7geb/) •
> 
> Great to hear. Give yourself some time and space to set it up to adjust to how it fits your work practices and then be judicious about the time spent “tweaking” it. Speaking from experience :-)

> **1Soundwave3** • [7 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/nj2pyfk/) •
> 
> Wow, well, soon you'll discover that Obsidian also gets slow to open on your phone when you have enough notes.
> 
> I remember some guy even coded up a paid widget to quickly capture to Obsidian.
> 
> Also, please keep in mind that plugins do get abandoned from time to time so get comfortable with fixing them by yourself when they eventually lose compatibility with Obsidian. Usually people put fixes in the GitHub issues of those abandoned repos.
> 
> But yeah, Obsidian is the best that we can have right now and I really like the fact that when I open my Obsidian every day - it's still **my** Obsidian vault and the front page of the app is **not** replaced with a fucking AI chat.

> **siglosi** • [6 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niyc6nl/) •
> 
> Took a while to get the hang of but me too
> 
> > **chinychon** • [5 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niyg9i9/) •
> > 
> > yeah I was experimenting for about 3 months before I finally made the switch

> **chichris** • [7 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niy6jys/) •
> 
> Moved from OneNote 2 weeks ago. Loving it.

> **Adventurous\_Shirt243** • [3 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niyo9oa/) •
> 
> Amazing setup. And unexpected Socotra mention.

> **ZubZero** • [3 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/nizsyej/) •
> 
> How do you capture hand written notes?

> **o-rka** • [3 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/nj18mbq/) •
> 
> What theme is this?
> 
> > **chinychon** • [3 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/nj1o8q3/) •
> > 
> > obsidian gruvbox

> **Total\_Recurrsion** • [3 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/nj3i9sz/) •
> 
> Amazing Layout. Obsidian looking better by the minute! lol notion really "lagging" behind (only if they would listen to their community more haha). Most of what I look for in a productivity app good utility. Notion AI sucks and is just a cash grab. Obsidian with a bit more can completely outshine it.
> 
> For now I might just use apple notes until satisfied. Great things are progressing!

> **zmrfzn** • [2 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niyqnmj/) •
> 
> Did you move all your existing notes from notion? How did you managerm the tasks/status mapping?
> 
> > **chinychon** • [4 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/niytr0b/) •
> > 
> > No I didn’t, I left a lot of it behind and copied only what I needed. transferring everything would be a lot of work haha.
> > 
> > Notes would be easy but old projects with mapping would be crazy

> **Substantial\_Bus5687** • [2 points](https://reddit.com/r/ObsidianMD/comments/1o3xo6g/comment/nj24g9g/) •
> 
> bases is such a game changer, but the one feature preventing me from making a full switch is gallery view