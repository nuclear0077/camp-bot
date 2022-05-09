/****** Object:  Table [dbo].[prefix_table_mobile_units_log_bot]    Script Date: 09.05.2022 19:24:55 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[prefix_table_mobile_units_log_bot](
	[User_id] [bigint] NOT NULL,
	[Date] [varchar](max) NULL,
	[Department] [float] NULL,
	[Type_Traning_id] [int] NOT NULL,
	[Faculties_id] [int] NOT NULL,
	[Directions_id] [int] NOT NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO


