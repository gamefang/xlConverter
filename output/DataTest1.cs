// xlConverter自动生成的脚本
using gamefang;

public class DataTest1
{
    public int key {get;}
    public string name {get;}
    public string tip {get;}
    public string[] mylist {get;}
    public string[] strlist {get;}
    public int value {get;}
    public string date {get;}
    public string  {get;}

    public DataTest1(int key)
    {
        this.key = key;
        this.name = ConfigManager.GetData<string>("test1",key,"name");
        this.tip = ConfigManager.GetData<string>("test1",key,"tip");
        this.mylist = ConfigManager.GetData<string[]>("test1",key,"mylist");
        this.strlist = ConfigManager.GetData<string[]>("test1",key,"strlist");
        this.value = ConfigManager.GetData<int>("test1",key,"value");
        this.date = ConfigManager.GetData<string>("test1",key,"date");
        this. = ConfigManager.GetData<string>("test1",key,"");
    }

}
