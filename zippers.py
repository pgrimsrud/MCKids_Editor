import tkinter as tk
from tkinter import messagebox


class ZipperStage:
    def __init__(self, stage_id):
        self.stage_id = stage_id
        self.zippers = []

    def get_data(self):
        data = [0xFE, self.stage_id]
        for zipper in self.zippers:
            data += zipper.get_data()

        return data

    def add_zipper(self, zipper):
        self.zippers.append(zipper)


class ZipperDefinition:
    def __init__(self, target_stage, x, y):
        self.target_stage = target_stage
        self.x = x
        self.y = y

    def get_data(self):
        return [self.target_stage, self.x, self.y, 0x00]


class ZipperMap:
    SIZE_LIMIT = 0x0152

    def __init__(self, rom_file):
        self.rom_file = rom_file
        self.stages = []
        self.load_data(rom_file.banks[1][0x13EE:0x13EE + ZipperMap.SIZE_LIMIT])

    def add_zipper(self, stage_id, target_stage, x, y):
        stage = self.get_stage_by_id(stage_id)
        space_needed = 4 if stage is None or len(stage.zippers) == 0 else 6
        if self.get_size() + space_needed > ZipperMap.SIZE_LIMIT:
            messagebox.showerror("Error", "There is not enough space to add another zipper.")
            return

        zipper = ZipperDefinition(target_stage, x, y)
        if stage is None:
            stage = ZipperStage(stage_id)
            self.stages.append(stage)

        stage.add_zipper(zipper)

    def get_stage_by_id(self, stage_id):
        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        return None

    def get_size(self):
        stages_with_zippers = len(list(filter(lambda s: len(s.zippers) > 0, self.stages)))
        total_number_of_zippers = 0
        for stage in self.stages:
            total_number_of_zippers += len(stage.zippers)

        return stages_with_zippers * 2 + total_number_of_zippers * 4 + 1

    def get_zipper_by_index(self, index):
        count = 0
        stage = 0
        while count + len(self.stages[stage].zippers) <= index:
            count += len(self.stages[stage].zippers)
            stage += 1
        return self.stages[stage].zippers[index - count]

    def remove_zipper_by_index(self, index):
        count = 0
        stage = 0
        while count + len(self.stages[stage].zippers) <= index:
            count += len(self.stages[stage].zippers)
            stage += 1

        self.stages[stage].zippers.remove(self.stages[stage].zippers[index - count])

    def get_data(self):
        data = []
        stages_with_zippers = len(self.stages.filter(lambda s: len(s.zippers) > 0))
        for stage in stages_with_zippers:
            data += stage.get_data()
        return data

    def load_data(self, data):
        ptr = 0
        self.stages = []
        while True:
            if data[ptr] != 0xFE:
                return

            stage = ZipperStage(data[ptr+1])
            ptr += 2
            while data[ptr] not in [0xFE, 0xFF]:
                stage.add_zipper(ZipperDefinition(data[ptr], data[ptr+1], data[ptr+2]))
                ptr += 4
            self.stages.append(stage)


class ZipperMapEditor:
    def __init__(self, parent, editor):
        self.target_stage = tk.StringVar()
        self.target_x = tk.StringVar()
        self.target_y = tk.StringVar()
        self.editor = editor
        self.map = ZipperMap(editor.rom_file)
        self.current_zipper = None

        self.window = tk.Toplevel(parent)
        self.window.geometry("475x210")

        zipper_frame = tk.Frame(self.window)
        self.zipper_list = tk.Listbox(zipper_frame, width=25, height=10, selectmode=tk.SINGLE)
        scrollbar = tk.Scrollbar(zipper_frame, orient="vertical", command=self.zipper_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.zipper_list.config(yscrollcommand=scrollbar.set)
        self.zipper_list.pack(side=tk.RIGHT, fill=tk.Y)
        self.zipper_list.bind('<<ListboxSelect>>', self.select_zipper)
        zipper_frame.grid(row=0, column=0, rowspan=4, padx=10, pady=10)

        tk.Label(self.window, text="Used space:").grid(row=0, column=1)
        self.used_space_lbl = tk.Label(self.window, text="")
        self.used_space_lbl.grid(row=0, column=2)
        tk.Label(self.window, text="Target stage ID:").grid(row=1, column=1)
        tk.Entry(self.window, textvariable=self.target_stage, width=5).grid(row=1, column=2)
        tk.Label(self.window, text="Target position:").grid(row=2, column=1)
        tk.Entry(self.window, textvariable=self.target_x, width=4).grid(row=2, column=2)
        tk.Entry(self.window, textvariable=self.target_y, width=4).grid(row=2, column=3)
        button_frame = tk.Frame(self.window)
        tk.Button(button_frame, text="Place", command=self.place_zipper).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Add zipper", command=self.add_zipper).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Remove zipper", command=self.remove_zipper).pack(side=tk.LEFT, padx=5)
        button_frame.grid(row=3, column=1, columnspan=3)

        self.populate_zipper_list()
        self.update_used_space()

    def populate_zipper_list(self):
        self.zipper_list.delete(0, tk.END)

        index = 0
        for stage in self.map.stages:
            zipper_no = 1
            for zipper in stage.zippers:
                self.zipper_list.insert(index, f'Stage {stage.stage_id}: zipper {zipper_no}')
                zipper_no += 1
                index += 1

    def select_zipper(self, event):
        tup = self.zipper_list.curselection()
        if len(tup) == 1:
            selected_zipper = tup[0]
            self.current_zipper = self.map.get_zipper_by_index(selected_zipper)
            self.target_stage.set(self.current_zipper.target_stage)
            self.target_x.set(self.current_zipper.x)
            self.target_y.set(self.current_zipper.y)

    def add_zipper(self):
        self.map.add_zipper(self.editor.current_stage, self.editor.current_stage, 0, 0)
        self.update_used_space()
        self.populate_zipper_list()

    def remove_zipper(self):
        tup = self.zipper_list.curselection()
        if len(tup) == 1:
            selected_zipper = tup[0]
            self.map.remove_zipper_by_index(selected_zipper)
            self.current_zipper = None
            self.update_used_space()
            self.populate_zipper_list()

    def update_used_space(self):
        used = self.map.get_size()
        self.used_space_lbl.config(text=f'{used}/{ZipperMap.SIZE_LIMIT} bytes')

    def place_zipper(self):
        self.editor.set_next_click_callback(self.set_zipper_data)

    def set_zipper_data(self, x, y):
        self.current_zipper.target_stage = self.editor.current_stage
        self.current_zipper.x = x
        self.current_zipper.y = y
        self.select_zipper(None)
        self.save_to_rom()

    def save_to_rom(self):
        ptr = 0x13EE
        rom = self.editor.rom_file.banks[1]
        for stage in self.map.stages:
            rom[ptr] = 0xFE
            rom[ptr+1] = stage.stage_id
            ptr += 2
            for zipper in stage.zippers:
                rom[ptr] = zipper.target_stage
                rom[ptr+1] = zipper.x
                rom[ptr+2] = zipper.y
                rom[ptr+3] = 0x00
                ptr += 4
        rom[ptr] = 0xFF
